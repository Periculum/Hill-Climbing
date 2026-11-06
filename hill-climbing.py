#!/usr/bin/env python3

import argparse
import math
import random
from pathlib import Path


class HillClimbing:
    def __init__(self, trigram_file, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                 restarts=20, steps=2500):
        self.alphabet = alphabet
        self.restarts = restarts
        self.steps = steps
        self.trigrams = self.load_trigrams(trigram_file)

    def normalize(self, text):
        return (text.upper().replace("Ä", "AE").replace("Ö", "OE")
                .replace("Ü", "UE"))

    def load_trigrams(self, filename):
        # Häufigkeiten aus einer deutschen Trigrammstatistik laden
        trigrams = {}

        with open(filename, encoding="utf-8") as file:
            for line in file:
                parts = line.split()
                if len(parts) != 2:
                    continue

                gram, frequency = parts
                gram = self.normalize(gram)

                if len(gram) == 3 and all(c in self.alphabet for c in gram):
                    trigrams[gram] = math.log(int(frequency))

        if not trigrams:
            raise ValueError("Keine gültigen Trigramme gefunden.")

        return trigrams

    def decrypt(self, ciphertext, key):
        # Jeder Buchstabe des Geheimtexts bekommt einen Klartextbuchstaben
        return ciphertext.translate(str.maketrans(self.alphabet, "".join(key)))

    def decrypt_transposition(self, ciphertext, key):
        # Spalten in der Reihenfolge des Schlüssels wieder füllen
        width = len(key)
        rows, extra = divmod(len(ciphertext), width)
        columns = [""] * width
        offset = 0

        for col in key:
            length = rows + (col < extra)
            columns[col] = ciphertext[offset:offset + length]
            offset += length

        # Ursprüngliche Zeilenfolge wiederherstellen
        return "".join(columns[i % width][i // width]
                       for i in range(len(ciphertext)))

    def evaluate(self, plaintext):
        # Summe der logarithmierten Häufigkeiten aller Dreierfolgen
        return sum(self.trigrams.get(plaintext[i:i+3], 0)
                   for i in range(len(plaintext) - 2))

    def hill_climbing(self, ciphertext, key_length=26, transposition=False):
        if transposition:
            print(f"\nSchlüssellänge {key_length}:")

        # Leerzeichen und Satzzeichen für die Bewertung entfernen
        letters = "".join(c for c in ciphertext if c in self.alphabet)
        decrypt_function = self.decrypt_transposition if transposition else self.decrypt
        symbols = list(range(key_length)) if transposition else list(self.alphabet)
        best_key = None
        best_score = float("-inf")
        attempts = 0

        for run in range(self.restarts):
            # Mit einem zufälligen Schlüssel beginnen
            key = symbols.copy()
            random.shuffle(key)
            score = self.evaluate(decrypt_function(letters, key))

            for _ in range(self.steps):
                # Zwei zufällige Positionen des Schlüssels vertauschen
                a, b = random.sample(range(len(key)), 2)
                key[a], key[b] = key[b], key[a]
                new_score = self.evaluate(decrypt_function(letters, key))
                attempts += 1

                if new_score > score:
                    # Die Veränderung verbessert den Klartext
                    score = new_score
                else:
                    # Die Veränderung rückgängig machen
                    key[a], key[b] = key[b], key[a]

            if score > best_score:
                best_score = score
                best_key = key.copy()

            print(f"Neustart {run + 1}/{self.restarts}: "
                  f"{attempts} Versuche, beste Bewertung {best_score:.2f}")

        return best_key, best_score, attempts

    def print_result(self, ciphertext, letters, key, score, attempts, transposition):
        print(f"\nVersuche insgesamt: {attempts}")
        print(f"Beste Bewertung:  {score:.2f}")

        if transposition:
            print("Schlüssellänge:", len(key))
            print("Spaltenreihenfolge:", tuple(col + 1 for col in key))
            plaintext = self.decrypt_transposition(letters, key)
        else:
            print("Geheimtextalphabet:", self.alphabet)
            print("Klartextalphabet: ", "".join(key))
            plaintext = self.decrypt(ciphertext, key)

        print("\nBester Klartext:\n", plaintext)

    def solve(self, ciphertext, transposition=False, min_key=4, max_key=12):
        letters = "".join(c for c in ciphertext if c in self.alphabet)
        if len(letters) < 3:
            raise ValueError("Der Geheimtext muss mindestens drei Buchstaben enthalten")

        if transposition:
            if min_key < 2 or max_key < min_key or min_key > len(letters):
                raise ValueError("Ungültiger Bereich für die Schlüssellänge")
            key_lengths = range(min_key, min(max_key, len(letters)) + 1)
        else:
            key_lengths = [len(self.alphabet)]

        best_key = None
        best_score = float("-inf")
        attempts = 0

        for key_length in key_lengths:
            key, score, count = self.hill_climbing(ciphertext, key_length, transposition)
            attempts += count

            if score > best_score:
                best_key = key
                best_score = score

        self.print_result(ciphertext, letters, best_key, best_score, attempts, transposition)


def main():
    # Argumentenparser
    parser = argparse.ArgumentParser()
    parser.add_argument("ciphertext", help="Datei mit dem Geheimtext")
    parser.add_argument("--trigrams", default=Path(__file__).with_name("german_trigrams.txt"))
    parser.add_argument("--restarts", type=int, default=20)
    parser.add_argument("--steps", type=int, default=2500)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--type", choices=["substitution", "transposition"],
                        default="substitution")
    parser.add_argument("--min-key", type=int, default=4)
    parser.add_argument("--max-key", type=int, default=12)
    args = parser.parse_args()

    if args.restarts < 1 or args.steps < 1:
        parser.error("--restarts und --steps müssen positiv sein")

    random.seed(args.seed)

    with open(args.ciphertext, encoding="utf-8-sig") as file:
        ciphertext = file.read()

    solver = HillClimbing(args.trigrams, restarts=args.restarts, steps=args.steps)

    try:
        solver.solve(ciphertext, args.type == "transposition", args.min_key, args.max_key)
    except ValueError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
