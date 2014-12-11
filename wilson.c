#include <math.h>

#define PI 3.14159265359

// http://stackoverflow.com/questions/10029588/python-implementation-of-the-wilson-score-interval

int sign(float x);
float normcdfi(float p, float mu, float sigma2);

float binconf(int p, int n, float c, float *theta_low, float *theta_high)
{
    // default: c=0.95
    float N = p + n;

    if (N == 0.0) return (0.0, 1.0);

    p = p / N;
    float z = normcdfi(1 - 0.5 * (1-c), 0.0, 1.0);      //default: mu=0.0, sigma2=1.0

    float a1 = 1.0 / (1.0 + z * z / N);
    float a2 = p + z * z / (2 * N);
    float a3 = z * sqrt(p * (1-p) / N + z * z / (4 * N * N));

    *theta_low  = a1 * (a2 - a3);
    *theta_high = a1 * (a2 + a3);
}

float erfi(float x)
{
    //Approximation to inverse error function
    
    float a = 0.147; // MAGIC!!!
    float a1 = log(1 - x * x);
    float a2 = (2.0 / (PI * a) + a1 / 2.0);

    return (sign(x) * sqrt( sqrt(a2 * a2 - a1 / a) - a2 ));
}

int sign(float x)
{
    if (x < 0)  return -1;
    if (x == 0) return 0;
    if (x > 0)  return 1;
}

float normcdfi(float p, float mu, float sigma2)
{
    //Inverse CDF of normal distribution
    //default: mu=0.0, sigma2=1.0
    if (mu == 0.0 && sigma2 == 1.0)
        //return sqrt(2) * erfi(2 * p - 1);
        return 1.4142135623730951 * erfi(2 * p - 1);
    else
        return mu + sqrt(sigma2) * normcdfi(p, mu, sigma2);      //default: mu=0.0, sigma2=1.0
}