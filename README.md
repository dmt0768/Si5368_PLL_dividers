# Si5368_PLL_dividers
The repository contains algorith of calculation of PLL divers. Si5368 is used

## Description
The Si5368 is a jitter-attenuating precision clock multiplier for applications requiring sub 1 ps rms jitter performance. The Si5368 is based on PLL. Buying Si5368 Evaluation Board you get one and some programs for adjusting the device. But it is only the test programs and it is impissoble to use them on production. So you have to write your own programs. The most difficult task is divdiders calculation. That's why this repository is created.

## Si5358 divers

The scheme of Si5368's PLL:

![PLL](https://github.com/dmt0768/Si5368_PLL_dividers/blob/main/images/изображение_2021-02-01_145832.png)


The limitaitions of PLL's:

![PLL_lim](https://github.com/dmt0768/Si5368_PLL_dividers/blob/main/images/изображение_2021-02-01_145900.png)

The divers' limitations:

![PLL_lim](https://github.com/dmt0768/Si5368_PLL_dividers/blob/main/images/изображение_2021-02-01_145921.png)

## How to use

You don't need in any python libs. Just download div_cal3 file and launch it with Python.

```
python div_calc3.py
```
