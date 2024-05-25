import string
import time


def load_words(file_path):
    with open(file_path, "r") as file:
        words = []
        lines = file.readlines()
        for line in lines:
            words.append(line.replace("\n", ""))
    return words


def calculate_letter_scores(words):
    letter_counts = {}
    total_letters = 0
    for word in words:
        for letter in word:
            if letter in letter_counts:
                letter_counts[letter] += 1
            else:
                letter_counts[letter] = 1
            total_letters += 1
    letter_scores = {
        letter: count / total_letters for letter, count, in letter_counts.items()
    }
    return letter_scores


words = load_words("valid-wordle-words.txt")
letter_scores = calculate_letter_scores(words)


class Guesser:
    # Known included letter = KI letter = letter confirmed in spot
    # Unknown included letter = UI letter = letter in word, unknown position
    # Not included letter = NI letter = letter not in word
    def __init__(self, word) -> None:
        self.valid_words = load_words("valid-wordle-words.txt")
        self.available_words = self.valid_words
        self.letter_scores = calculate_letter_scores(self.available_words)
        self.letter_information = {key: None for key in string.ascii_lowercase}
        self.target_word = word
        self.used_letters = []

    def update_available_words(self):
        for letter, information in self.letter_information.items():
            if information is not None:
                if (
                    information > 5
                ):  # TODO: Make sure Guesser knows not to repeat a UI letter in the same position
                    self.available_words = [
                        word
                        for word in self.available_words
                        if letter in word and word[information - 6] is not letter
                    ]
                elif information == -1:
                    self.available_words = [
                        word for word in self.available_words if letter not in word
                    ]
                else:
                    self.available_words = [
                        word
                        for word in self.available_words
                        if word[information] == letter
                    ]

    def guess(self):

        best_word = ("", -1)
        for word in self.available_words:
            value = 0
            temp_used_letters = []
            for letter in word:
                if letter not in self.used_letters and letter not in temp_used_letters:
                    value += self.letter_scores[letter]
                    temp_used_letters.append(letter)
            if value > best_word[1]:
                best_word = (word, value)

        for letter in best_word[0]:
            self.used_letters.append(letter)
        print("Guess: ", best_word[0])
        return best_word[0]

    def check(self, word):
        if word == self.target_word:
            print("Wordlebot wins!")
            return 0
        for i in range(len(word)):
            if word[i] == self.target_word[i]:
                self.letter_information[word[i]] = i
            elif word[i] in self.target_word:
                self.letter_information[word[i]] = i + 6
            else:
                self.letter_information[word[i]] = -1
        self.update_available_words()
        return -1

    def solve(self):
        attempt = 1
        solved = -1
        print("The target word is: ", self.target_word)
        counter = 0
        while counter < 6 and solved == -1:
            guess = self.guess()
            solved = self.check(guess)
            counter += 1


# TODO: Fix double letters

guesser = Guesser("treat")
start = time.perf_counter()
guesser.solve()
end = time.perf_counter()
print(f"It took Wordlebot {end-start} seconds to solve this puzzle!")
