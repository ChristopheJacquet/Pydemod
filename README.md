Pydemod
-------

Pydemod is a set of Python 3 libraries and tools for demodulating radio signals. It does not intend to compete with full-featured packages such as GNU Radio. Instead, it strives to allow radio enthusiasts to gain hands-on experience with modulation schemes.

Pydemod relies on [NumPy](http://numpy.scipy.org/)/[SciPy](http://www.scipy.org/).

On Ubuntu use 

```
pipx install scipy --include-deps
```

Currently, the released modules include:
 
 * physical layer:
   * phase demodulation (_naïve_)
   * Manchester decoding
   * basic logical levels (TTL-like) decoding and clock synchronization
 * data link layer:
   * synchronization and error detection for polynomial codes
   * full implementation of [RDS](http://en.wikipedia.org/wiki/Radio_Data_System) and [AMSS](http://en.wikipedia.org/wiki/Amplitude_modulation_signalling_system) codes
   * CRC calculation
 * application layer:
   * functional AMSS decoder
   * functional temperature & humidity sensor decoder (supports protocols TX29 and Conrad) → [see blog post (in French)](https://jacquet.xyz/articles/2011/10/Decodage-capteur-thermo-hygro-TFA/)
     * You can very easily receive signals using an RTL-SDR dongle, using a command like this: `rtl_fm -M am -f 868.4M -s 160k -  | ./decode_weather.py --protocol tx29 --squelch 4000 --rawle -`

RDS bitstream decoding from wave file captured by the RTL-SDR dongle can be done using (file name and path is an example)

`rtl_fm  -f 104900k -s 228k -E wav /tmp/104900.wav` 

If your version of `rtl_fm` (check `rtl_fm --help`) does not understand the `-E wav` parameter, use sox to do it for you: 

`rtl_fm  -f 104900k -s 228k -E wav - | sox -t raw -r 228k -es -b 16 - -c 1 /tmp/104900.wav`

Then load your file and get the following output

```
./demodulate_rds.py --input "/tmp/104900.wav" --output "/tmp/104900.rds"
Sample rate: 228000 Hz, duration: x.xxx s
```

The `104900.rds` bitstream file should then look like 

```
cat /tmp/104900.rds 
1111001111111100000101110010010110111011010101011011000001010
```

This file you can load into `redsea` or `RDSSpy`.

Note that currently only 228k (= 4x 57 kHz) mpx files with an appropriate header can be used.

Pydemod is licensed under the terms of the [GNU GPL v3](https://www.gnu.org/copyleft/gpl.html).

----
_Pydemod is developed by [Christophe Jacquet](https://jacquet.xyz/), F8FTK/HB9ITK._
