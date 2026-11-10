# Hill-Climbing
A simple Hill-Climbing-Implementation to break monoalphabetic ciphers and transposition ciphers, written for a c't article. The Article was published online on heise+.

The program generates random keys, swaps positions and evaluates the resulting plaintext using trigram frequencies. Better solutions are kept, while random restarts help escape local maxima.

## Usage

Requires Python 3 and a trigram frequency file (`german_trigrams.txt`). The German trigram frequencies are available in the [torognes/enigma repository](https://github.com/torognes/enigma/blob/master/german_trigrams.txt).

**Monoalphabetic substitution:**

```bash
python3 hill_climbing.py cipher.txt
```

**Columnar transposition:**

```bash
python3 hill_climbing.py cipher.txt --type transposition
```

### Options

- `--type {substitution,transposition}` – Choose the cipher type (default: `substitution`).
- `--trigrams FILE` – Specify the trigram frequency file (default: `german_trigrams.txt`).
- `--restarts N` – Number of random restarts (default: `50`).
- `--steps N` – Number of key swaps per restart (default: `5000`).
- `--seed N` – Set a random seed for reproducible results.
- `--min-key N` – Minimum column count for transposition (default: `4`).
- `--max-key N` – Maximum column count for transposition (default: `12`).

**Note:** For transposition ciphers, remove spaces and punctuation before encryption. The trigram statistics should match the plaintext language.

## Copyright

Copyright ©️ 2026 Wilhelm Drehling, Heise Medien GmbH & Co. KG

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.
