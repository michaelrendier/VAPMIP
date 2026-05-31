/**
 * ble.ts — P.O.E. Pendant + EarPiece BLE connection
 *
 * Pendant SPP UUID: 00001101-0000-1000-8000-00805f9b34fb
 * EarPiece MAC:     11:94:AA:10:05:82 (F-SL001A)
 *
 * When pendant is in range: upgrades from JS engine to full monad.c.
 * When absent: JS engine fallback is transparent to the UI.
 */

import { BleManager, Device, State } from 'react-native-ble-plx';
import { Platform } from 'react-native';

const SPP_SERVICE  = '00001101-0000-1000-8000-00805f9b34fb';
const EARPIECE_MAC = '11:94:AA:10:05:82';

// Well-known pendant device name prefix (set in pendant firmware)
const PENDANT_NAME_PREFIX = 'Ptolemy';

export type BleStatus = 'idle' | 'scanning' | 'connecting' | 'connected' | 'error';

export interface PendantState {
  status:   BleStatus;
  device:   Device | null;
  isEarpiece: boolean;
}

export type OnResponse = (text: string) => void;
export type OnStatus   = (state: PendantState) => void;

export class PendantClient {
  private manager:    BleManager | null = null;
  private device:     Device | null     = null;
  private scanning:   boolean           = false;
  private onResponse: OnResponse | null = null;
  private onStatus:   OnStatus | null   = null;
  private _status:    BleStatus         = 'idle';
  private _isEarpiece = false;

  constructor(onResponse: OnResponse, onStatus: OnStatus) {
    this.onResponse = onResponse;
    this.onStatus   = onStatus;
    if (Platform.OS !== 'web') {
      this.manager = new BleManager();
    }
  }

  private _setState(status: BleStatus, device: Device | null = this.device): void {
    this._status = status;
    this.onStatus?.({ status, device, isEarpiece: this._isEarpiece });
  }

  async start(): Promise<void> {
    if (!this.manager) return; // web — no BLE
    const state = await this.manager.state();
    if (state !== State.PoweredOn) {
      this._setState('error');
      return;
    }
    this._scan();
  }

  private _scan(): void {
    if (!this.manager || this.scanning) return;
    this.scanning = true;
    this._setState('scanning');
    this.manager.startDeviceScan(null, null, (err, dev) => {
      if (err || !dev) return;
      const isPendant  = dev.name?.startsWith(PENDANT_NAME_PREFIX);
      const isEarpiece = dev.id === EARPIECE_MAC;
      if (isPendant || isEarpiece) {
        this._isEarpiece = !!isEarpiece && !isPendant;
        this._connect(dev);
      }
    });
    // Auto-stop scan after 15s
    setTimeout(() => this._stopScan(), 15000);
  }

  private _stopScan(): void {
    if (!this.scanning) return;
    this.manager?.stopDeviceScan();
    this.scanning = false;
    if (this._status === 'scanning') this._setState('idle');
  }

  private async _connect(dev: Device): Promise<void> {
    if (!this.manager) return;
    this._stopScan();
    this._setState('connecting', dev);
    try {
      const connected = await this.manager.connectToDevice(dev.id);
      await connected.discoverAllServicesAndCharacteristics();
      this.device = connected;
      this._setState('connected', connected);

      // Monitor disconnect
      connected.onDisconnected(() => {
        this.device = null;
        this._setState('idle');
        // Retry scan after 5s
        setTimeout(() => this._scan(), 5000);
      });

      // Monitor incoming characteristics for responses
      const services = await connected.services();
      for (const svc of services) {
        const chars = await svc.characteristics();
        for (const char of chars) {
          if (char.isNotifiable) {
            char.monitor((err, c) => {
              if (!err && c?.value) {
                const text = atob(c.value);
                this.onResponse?.(text);
              }
            });
          }
        }
      }
    } catch (_) {
      this._setState('error');
      setTimeout(() => this._scan(), 8000);
    }
  }

  async send(text: string): Promise<boolean> {
    if (!this.device || this._status !== 'connected') return false;
    try {
      const services = await this.device.services();
      for (const svc of services) {
        if (svc.uuid.toLowerCase().includes(SPP_SERVICE.slice(0, 8))) {
          const chars = await svc.characteristics();
          for (const char of chars) {
            if (char.isWritableWithResponse || char.isWritableWithoutResponse) {
              const encoded = btoa(text);
              await this.device.writeCharacteristicWithResponseForService(
                svc.uuid, char.uuid, encoded,
              );
              return true;
            }
          }
        }
      }
    } catch (_) {}
    return false;
  }

  get isConnected(): boolean { return this._status === 'connected'; }
  get status(): BleStatus    { return this._status; }

  destroy(): void {
    this._stopScan();
    this.device?.cancelConnection();
    this.manager?.destroy();
  }
}
