import json
import string
import time
from valid_answers import valid_answers
import numpy as np
from wordfreq import zipf_frequency


def load_words(file_path):
    with open(file_path, "r") as file:
        words = []
        lines = file.readlines()
        for line in lines:
            words.append(line.replace("\n", ""))
    return words


words = load_words("valid-wordle-words.txt")


class Guesser:
    def __init__(
        self, word, positional_weight, risk_reward_weight, starting_word
    ) -> None:
        self.all_words = load_words("valid-wordle-words.txt")
        self.remaining_answers = valid_answers
        self.letter_information = {key: None for key in string.ascii_lowercase}
        self.target_word = word
        self.used_letters = []
        self.guess_counter = 0
        self.solved = False
        self.positional_weight = positional_weight
        self.risk_reward_weight = risk_reward_weight
        self.starting_word = starting_word

    def update_remaining_answers(self):
        for letter, information in self.letter_information.items():
            if information is not None:
                if information > 4:
                    self.remaining_answers = [
                        word
                        for word in self.remaining_answers
                        if letter in word and word[information - 5] is not letter
                    ]
                elif information == -1:
                    self.remaining_answers = [
                        word for word in self.remaining_answers if letter not in word
                    ]
                else:
                    self.remaining_answers = [
                        word
                        for word in self.remaining_answers
                        if word[information] == letter
                    ]

    def expected_information(self, letter, position):
        # Of the remaining answers, how many have this letter? We're looking for half
        counter = 0
        positional_counter = 0
        for word in self.remaining_answers:
            if letter in word:
                counter += 1
                if word[position] == letter:
                    positional_counter += 1

        frequency = counter / len(self.remaining_answers)

        if counter > 0:
            positional_frequency = positional_counter / counter
        else:
            positional_frequency = 0

        base_information = 0.5 * (1 + np.cos(np.pi * (2 * frequency - 1)))

        positional_information = frequency * (
            1 + np.cos(np.pi * (2 * positional_frequency - 1))
        )
        positional_information = positional_information * self.positional_weight
        # if the letter in the word, we may get additional information if the letter is in the same spot

        return base_information, positional_information

    def guess(self, starting_word=None):
        best_word = ("", -1)
        for word in self.all_words:
            value = 0
            temp_used_letters = []
            for idx, letter in enumerate(word):
                if letter not in temp_used_letters and letter not in self.used_letters:

                    base_information, positional_information = (
                        self.expected_information(letter, idx)
                    )

                    if (
                        self.letter_information[letter] is not None
                        and self.letter_information[letter] > 5
                    ):  # if we've used the letter before but don't know the position, we only get positional information
                        value += positional_information
                    else:  # we haven't used this letter before
                        value += base_information + positional_information

                    temp_used_letters.append(letter)

            # if (
            #     word in self.remaining_answers
            # ):  # bonus for being an attempt at an actual answer
            #     value = value * 1.5

            if (
                word in self.remaining_answers and value == 0
            ):  # this will help to filter at the end, where the answer may not gain any more information
                value += self.risk_reward_weight

            if value > best_word[1]:
                best_word = (word, value)

        if starting_word is not None:
            best_word = (starting_word, 0)

        for letter in best_word[0]:
            self.used_letters.append(letter)

        self.guess_counter += 1
        return best_word[0]

    def check(self, word):
        if word == self.target_word:
            print("Wordlebot wins!")
            self.solved = True
            return

        for i in range(len(word)):
            if word[i] == self.target_word[i]:
                self.letter_information[word[i]] = i
            elif word[i] in self.target_word:
                self.letter_information[word[i]] = i + 5
            else:
                self.letter_information[word[i]] = -1

        self.update_remaining_answers()
        self.solved = False

    def solve(self):
        print("The target word is: ", self.target_word)

        guess = self.guess(self.starting_word)
        self.check(guess)
        print("Guess: ", guess)

        while self.solved == False:
            guess = self.guess()
            print("Guess: ", guess)
            self.check(guess)
            if self.guess_counter > 15:
                return 10000
        return self.guess_counter


def test(pos_weight, rr_weight, start_word):
    count = 0
    test_size = 200
    for idx, word in enumerate(valid_answers[1:test_size]):
        guesser = Guesser(
            word,
            positional_weight=pos_weight,
            risk_reward_weight=rr_weight,
            starting_word=start_word,
        )
        count += guesser.solve()
    return count / test_size


positional_weights = [0.5, 0.75, 1.0, 1.25, 1.5]
risk_reward_weights = [0.25, 1.0, 1.5, 2]
starting_words = ["slate", "adieu", "crate"]

results = {}

guesser = Guesser("risky", 0.75, 1.0, "crate")
guesser.solve()
# for pos_weight in positional_weights:
#     for rr_weight in risk_reward_weights:
#         for word in starting_words:
#             score = test(pos_weight=pos_weight, rr_weight=rr_weight, start_word=word)
#             results[f"{pos_weight}, {rr_weight}, {word}"] = score

# with open('results.txt', 'w') as file:
#      file.write(json.dumps(results))
