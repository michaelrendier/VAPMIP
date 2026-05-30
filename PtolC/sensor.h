/*
 * PtolC/sensor.h — Physical sensor bridge declarations.
 */

#ifndef PTOL_SENSOR_H
#define PTOL_SENSOR_H

#include <stdio.h>

/*
 * sensor_read - Read 8 sensor channels from live_state.json.
 *
 * path may be NULL or "" to use the default ~/.ptolemy/live_state.json.
 * channels_out must point to float[8].
 * Returns 1 on success, 0 on failure (channels zeroed on failure).
 */
int sensor_read(float *channels_out, const char *path);

/*
 * sensor_write - Write 8 sensor channels to live_state.json.
 *
 * Creates or overwrites the file. path as above.
 * Returns 1 on success, 0 on failure.
 */
int sensor_write(const float *channels, const char *path);

/*
 * sensor_print - Print sensor channel table to out (human-readable).
 */
void sensor_print(const float *channels, FILE *out);

#endif /* PTOL_SENSOR_H */
