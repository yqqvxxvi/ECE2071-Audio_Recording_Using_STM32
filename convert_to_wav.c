/*
File Header: convert_to_wav.c
Description: This program converts 12-bit ADC data from a binary file to a WAV file format.
It reads the ADC data, converts it to PCM format, and writes it to a WAV file with the specified parameters.

version 1.0:
Written by: Liew You Qing 33590400
Written on: 23/03/2025

version 1.0.5:
Last modified by: Liew You Qing 33590400
Last modified on: 07/04/2025
Description: Added error handling for file operations and memory allocation.
            Added comments.
            Added a function to write the WAV header.

version 1.1.0:
Last modified by: Naamjas Singh 34392017
Last modified on: 10/04/2025
Description: Added comments and function headers. 
*/

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

#define ADC_MAX         4095
#define PCM_MAX         32767
#define PCM_MIN        -32768
#define SAMPLE_RATE     6400
#define BITS_PER_SAMPLE 16
#define NUM_CHANNELS    1
#define HEADER_SIZE     44

//Declare function protypes
//Function takes in a pointer to a file, and an integer value for the size of the file in bytes
void write_wav_header(FILE *fp, int data_size);

//main function
int main(int argc, char *argv[]) {
    //check for valid number of arguments in command line
    if (argc < 3) {
        fprintf(stderr, "Usage: %s <input_file> <output_wav_file>\n", argv[0]);
        return 1;
    }

    const char *input_filename = argv[1];
    const char *output_filename = argv[2];

    //Opens file in read only, binary mode
    FILE *input = fopen(input_filename, "rb"); 
    if (!input) {
        perror("Error opening input file");
        return 1;
    }

    // Determine file size
    fseek(input, 0, SEEK_END);
    long file_size = ftell(input);
    fseek(input, 0, SEEK_SET); // reset file pointer to the beginning

    // Allocate memory for ADC data
    uint8_t *adc_data = (uint8_t*) malloc(file_size);
    if (!adc_data) {
        perror("Memory allocation failed");
        fclose(input);
        return 1;
    }

    // Read ADC data from file
    fread(adc_data, 1, file_size, input);
    fclose(input);

    // Convert and write WAV file
    FILE *output = fopen(output_filename, "wb");    
    if (!output) {
        perror("Error opening output file");
        free(adc_data);
        return 1;
    }

    //WAV Header and Data Conversion
    int num_samples = file_size / 2;  // 2 bytes per 12-bit ADC sample (sent as two bytes)
    write_wav_header(output, num_samples * 2); // 2 bytes per PCM sample

    //Converts ADC to PCM (scale) and write
    for (int i = 0; i < num_samples; i++) {
        uint16_t raw = adc_data[2*i] | (adc_data[2*i + 1] << 8);  // Little-endian 12-bit
        int16_t pcm = (int16_t)(((int32_t)raw * (PCM_MAX - PCM_MIN)) / ADC_MAX + PCM_MIN); //makes midpoint of ADC range into PCM 0
        fwrite(&pcm, sizeof(int16_t), 1, output);
    }

    fclose(output);
    free(adc_data);
    printf("WAV file '%s' generated successfully.\n", output_filename);
    return 0; // exit code = 0
}


/*
Function takes in a pointer to a file and writes the wav. file header into the file.

Parameters: 
FILE *fp: pointer to a file 
int data_size: Size of file in bytes (data is of type integer)

Returns: 
None.

Note: 
Function writes into the file pointed to by the file pointer (1st function argument)

Example usage:
    FILE *fp = fopen("audio.wav", "wb")     //write access to file in binary
    write_wav_header(fp, 80000)
*/
void write_wav_header(FILE *fp, int data_size) {
    int byte_rate = SAMPLE_RATE * NUM_CHANNELS * BITS_PER_SAMPLE / 8;
    int block_align = NUM_CHANNELS * BITS_PER_SAMPLE / 8;
    int total_size = data_size + HEADER_SIZE - 8;

    // Write "RIFF"
    fwrite("RIFF", 1, 4, fp);
    fwrite(&total_size, 4, 1, fp);       // Total size - 8
    fwrite("WAVE", 1, 4, fp);
    fwrite("fmt ", 1, 4, fp);

    //Declare variables used
    uint32_t subchunk1_size = 16;
    uint16_t audio_format = 1;
    uint16_t num_channels = NUM_CHANNELS;
    uint32_t sample_rate = SAMPLE_RATE;
    uint16_t block_align_val = block_align;
    uint16_t bits_per_sample = BITS_PER_SAMPLE;

    fwrite(&subchunk1_size, 4, 1, fp);     // Subchunk1Size
    fwrite(&audio_format, 2, 1, fp);       // PCM = 1
    fwrite(&num_channels, 2, 1, fp);
    fwrite(&sample_rate, 4, 1, fp);
    fwrite(&byte_rate, 4, 1, fp);
    fwrite(&block_align_val, 2, 1, fp);
    fwrite(&bits_per_sample, 2, 1, fp);

    // Write "data" subchunk
    fwrite("data", 1, 4, fp);
    fwrite(&data_size, 4, 1, fp);         // Subchunk2Size
}