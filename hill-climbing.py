#!/usr/bin/env python3

import argparse
import math
import random
from pathlib import Path

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def normalize(text):
    return (text.upper().replace("Ä", "AE").replace("Ö", "OE")
            .replace("Ü", "UE").replace("ẞ", "SS"))


def load_trigrams(filename):
    # Häufigkeiten aus einer allgemeinen deutschen Trigrammstatistik laden.
    trigrams = {}

    with open(filename, encoding="utf-8") as file:
        for line in file:
            parts = line.split()
            if len(parts) != 2:
                continue

            gram, frequency = parts
            gram = normalize(gram)

            if len(gram) == 3 and all(c in ALPHABET for c in gram):
                trigrams[gram] = math.log(int(frequency))

    if not trigrams:
        raise ValueError("Keine gültigen Trigramme gefunden.")

    return trigrams


def decrypt(ciphertext, key):
    # Jeder Buchstabe des Geheimtexts bekommt einen Klartextbuchstaben.
    return ciphertext.translate(str.maketrans(ALPHABET, "".join(key)))


def evaluate(plaintext, trigrams):
    # Summe der logarithmierten Häufigkeiten aller Dreierfolgen.
    return sum(trigrams.get(plaintext[i:i+3], 0)
               for i in range(len(plaintext) - 2))


def hill_climbing(ciphertext, trigrams, restarts=50, steps=5000):
    # Leerzeichen und Satzzeichen für die Bewertung entfernen.
    letters = "".join(c for c in ciphertext if c in ALPHABET)
    best_key = None
    best_score = float("-inf")
    attempts = 0

    for run in range(restarts):
        # Mit einem zufälligen Schlüssel beginnen
        key = list(ALPHABET)
        random.shuffle(key)
        score = evaluate(decrypt(letters, key), trigrams)

        for _ in range(steps):
            # Zwei zufällige Buchstaben des Schlüssels vertauschen
            a, b = random.sample(range(len(ALPHABET)), 2)
            key[a], key[b] = key[b], key[a]
            new_score = evaluate(decrypt(letters, key), trigrams)
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

        print(f"Neustart {run + 1}/{restarts}: " f"{attempts} Versuche, beste Bewertung {best_score:.2f}")

    return best_key, best_score, attempts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ciphertext", help="Datei mit dem Geheimtext")
    parser.add_argument("--trigrams", default=Path(__file__).with_name("german_trigrams.txt"))
    parser.add_argument("--restarts", type=int, default=50)
    parser.add_argument("--steps", type=int, default=5000)
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()

    if args.restarts < 1 or args.steps < 1:
        parser.error("--restarts und --steps müssen positiv sein")

    random.seed(args.seed)

    with open(args.ciphertext, encoding="utf-8-sig") as file:
        ciphertext = normalize(file.read())

    if sum(c in ALPHABET for c in ciphertext) < 3:
        parser.error("Der Geheimtext muss mindestens drei Buchstaben enthalten")

    trigrams = load_trigrams(args.trigrams)
    key, score, attempts = hill_climbing(ciphertext, trigrams, args.restarts,
                                         args.steps)

    print(f"\nVersuche insgesamt: {attempts}")
    print(f"Beste Bewertung:  {score:.2f}")
    print("Geheimtextalphabet:", ALPHABET)
    print("Klartextalphabet: ", "".join(key))
    print("\nBester Klartext:\n", decrypt(ciphertext, key))


if __name__ == "__main__":
    main()
