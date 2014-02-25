Pydemod
-------

Pydemod is a set of Python libraries and tools for demodulating radio signals. It does not intend to compete with full-featured packages such as GNU Radio. Instead, it strives to allow radio enthusiasts to gain hands-on experience with modulation schemes.

Pydemod relies on [NumPy](http://numpy.scipy.org/)/[SciPy](http://www.scipy.org/).

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
  * functional TFA temperature & humidity sensor decoder (should work for other Instant Transmission IT+ 868 MHz systems, such as LaCrosse ones) → [see blog post (in French)](http://www.jacquet80.eu/blog/post/2011/10/Decodage-capteur-thermo-hygro-TFA)

----
_Pydemod is developed by [Christophe Jacquet](http://www.jacquet80.eu/), [F8FTK](http://f8ftk.tk)._
