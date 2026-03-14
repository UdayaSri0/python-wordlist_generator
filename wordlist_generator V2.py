#!/usr/bin/env python3
"""
Deep User Profiling Wordlist Generator (Improved)
Generates a highly targeted wordlist based on detailed user profiling.
"""

import itertools
import os
import sys
import time
from collections import defaultdict
from datetime import datetime

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
# Common symbols to append if enabled
def unique_preserve_order(values):
    """Return values with duplicates removed while preserving order."""
    return list(dict.fromkeys(values))

SYMBOLS = unique_preserve_order(['!', '@', '#', '$', '%', '^', '&', '*', '?', '.'])

# Common number suffixes to append if enabled
NUMBERS = unique_preserve_order([
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    '01', '07', '10', '12',
    '00', '11', '22', '33', '44', '55', '66', '77', '88', '99',
    '111', '123', '321', '420', '666', '777', '888', '999',
    '1234', '12345', '123456',
    '2020', '2021', '2022', '2023', '2024', '2025', '2026', '2027'
])

# Separators to insert between combined words (if enabled)
SEPARATORS = ['', '_', '-', '.', '@', '#', '$']  # empty = no separator

# Leet mapping (case‑insensitive, applied to original case)
LEET_MAP = {
    'a': '@',
    'e': '3',
    'i': '1',
    'o': '0',
    's': '$'
}

# Tags that are considered "date‑like" and may need special handling
DATE_TAGS = {
    'birth_day', 'birth_month', 'birth_year', 'birth_date_combo',
    'partner_birth_day', 'partner_birth_month', 'partner_birth_year', 'partner_birth_date_combo',
    'anniversary_day', 'anniversary_month', 'anniversary_year', 'anniversary_date_combo'
}

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def leet_transform(word):
    """Apply basic leet substitution to a word."""
    if not word:
        return word
    return ''.join(LEET_MAP.get(ch.lower(), ch) for ch in word)

def case_variations(word):
    """Return a set of common case variations for a word."""
    vars_set = {word, word.lower(), word.upper(), word.title(), word.swapcase()}
    vars_set.discard('')
    return vars_set

def parse_date(day, month, year, prefix=''):
    """
    Given day, month, year strings (may be empty), return a dictionary
    of tags to list of values for date‑related entries.
    If prefix is given, it is prepended to tag names.
    """
    results = defaultdict(list)
    if day:
        day = day.zfill(2)
        results[prefix + 'day'].append(day)
    if month:
        month = month.zfill(2)
        results[prefix + 'month'].append(month)
    if year:
        year_full = year.zfill(4) if len(year) <= 4 else year
        results[prefix + 'year'].append(year_full)
        if len(year_full) == 4:
            results[prefix + 'year'].append(year_full[2:])  # two‑digit year
    # Combined forms (only if both day and month, or all three)
    if day and month:
        results[prefix + 'date_combo'].append(day + month)      # DDMM
        results[prefix + 'date_combo'].append(month + day)      # MMDD
        if year:
            results[prefix + 'date_combo'].append(day + month + year_full)  # DDMMYYYY
            results[prefix + 'date_combo'].append(month + day + year_full)  # MMDDYYYY
    return results

def ask_string(prompt):
    """Ask for a single string, return stripped value or None if empty."""
    val = input(prompt).strip()
    return val if val else None

def ask_multiple(prompt):
    """Ask for comma‑separated values, return list of stripped non‑empty strings."""
    val = input(prompt).strip()
    if not val:
        return []
    return [v.strip() for v in val.split(',') if v.strip()]

def ask_yes_no(prompt, default='y'):
    """Ask a yes/no question, return True for yes, False for no."""
    val = input(prompt).strip().lower()
    if not val:
        return default == 'y'
    return val.startswith('y')

def ask_date(prompt_prefix):
    """Ask for day, month, year and return processed date dict."""
    print(f"\n{prompt_prefix} (press Enter to skip any field)")
    day = ask_string("  Day (DD): ")
    month = ask_string("  Month (MM): ")
    year = ask_string("  Year (YYYY): ")
    return parse_date(day, month, year)

# ----------------------------------------------------------------------
# Profile class
# ----------------------------------------------------------------------
class Profile:
    """Holds all collected user data as lists of strings per tag."""
    def __init__(self):
        self.data = defaultdict(list)   # tag -> list of strings
        self.append_symbols = True
        self.append_numbers = True
        self.use_separators = True
        self.min_len = 6
        self.max_len = 16

    def add(self, tag, value):
        """Add a single value to a tag."""
        if value:
            self.data[tag].append(value)

    def add_multiple(self, tag, values):
        """Add multiple values to a tag."""
        if values:
            self.data[tag].extend(values)

    def extend(self, tag, values):
        """Extend a tag with a list of values."""
        if values:
            self.data[tag].extend(values)

    def any_data(self):
        """Return True if at least one tag has data."""
        return any(self.data.values())

    def display_summary(self):
        """Print a summary of collected data."""
        print("\n" + "="*60)
        print("COLLECTED DATA SUMMARY")
        print("="*60)
        for tag, values in sorted(self.data.items()):
            if values:
                print(f"{tag:25}: {', '.join(values)}")
        print(f"\nModifiers:")
        print(f"  Append symbols : {self.append_symbols}")
        print(f"  Append numbers : {self.append_numbers}")
        print(f"  Use separators : {self.use_separators}")
        print(f"  Length range   : {self.min_len} - {self.max_len}")
        print("="*60)

# ----------------------------------------------------------------------
# Questionnaire
# ----------------------------------------------------------------------
def run_questionnaire():
    """Interactive data collection, returns a Profile object."""
    profile = Profile()

    print("\n" + "="*60)
    print("DEEP USER PROFILING WORDLIST GENERATOR (IMPROVED)")
    print("="*60)
    print("Enter information about the target. Press Enter to skip any field.")
    print("For multiple entries, separate with commas.\n")

    # Personal Info
    print("\n--- PERSONAL INFO ---")
    profile.add('first_name', ask_string("First Name: "))
    profile.add('middle_name', ask_string("Middle Name: "))
    profile.add('last_name', ask_string("Last Name: "))
    profile.add('nickname', ask_string("Nickname: "))
    profile.add('username', ask_string("Username (if known): "))
    email = ask_string("Email address (local part only, before @): ")
    if email:
        profile.add('email_local', email)
        # Also add the part before any dot as a variation
        if '.' in email:
            profile.add('email_local', email.split('.')[0])

    # Date of Birth
    dob_data = ask_date("Date of Birth")
    for tag, values in dob_data.items():
        profile.extend(tag, values)

    # Family & Relationships
    print("\n--- FAMILY & RELATIONSHIPS ---")
    profile.add('partner_name', ask_string("Partner's Name: "))
    profile.add('partner_nickname', ask_string("Partner's Nickname: "))
    partner_dob = ask_date("Partner's Date of Birth")
    for tag, values in partner_dob.items():
        profile.extend('partner_' + tag, values)

    profile.add_multiple('child_name', ask_multiple("Child(ren)'s Name(s): "))
    profile.add_multiple('child_nickname', ask_multiple("Child(ren)'s Nickname(s): "))
    profile.add_multiple('parent_name', ask_multiple("Parent(s)' Name(s): "))
    profile.add_multiple('pet_name', ask_multiple("Pet(s)' Name(s): "))

    # Anniversary (if any)
    print("\n--- ANNIVERSARY / SPECIAL DATE ---")
    anniv_data = ask_date("Anniversary or other special date")
    for tag, values in anniv_data.items():
        profile.extend('anniversary_' + tag, values)

    # Education & Career
    print("\n--- EDUCATION & CAREER ---")
    profile.add('company', ask_string("Company/Workspace Name: "))
    profile.add('school', ask_string("School Name: "))
    profile.add('campus', ask_string("Campus Name: "))
    profile.add('university', ask_string("University: "))
    profile.add('teacher', ask_string("Favorite/Memorable Teacher's Name: "))

    # Interests & Geography
    print("\n--- INTERESTS & GEOGRAPHY ---")
    profile.add('hometown', ask_string("Hometown: "))
    profile.add('city', ask_string("Current City: "))
    profile.add('street', ask_string("Street Name: "))
    profile.add('sports_team', ask_string("Favorite Sports Team: "))
    profile.add('color', ask_string("Favorite Color: "))
    profile.add('band', ask_string("Favorite Band/Artist: "))
    profile.add('movie', ask_string("Favorite Movie/Character: "))
    profile.add('car', ask_string("Car Brand/Model: "))
    profile.add('food', ask_string("Favorite Food: "))
    profile.add('place', ask_string("Favorite Place: "))

    # Numbers & IDs
    print("\n--- NUMBERS & IDs ---")
    profile.add_multiple('phone', ask_multiple("Phone Number(s): "))
    profile.add_multiple('id_number', ask_multiple("Important ID Numbers (e.g., student/employee ID, national ID): "))
    profile.add('zip', ask_string("Postal/Zip Code: "))
    profile.add_multiple('lucky_number', ask_multiple("Personal 'Lucky' Numbers: "))

    # Modifiers
    print("\n--- MODIFIERS ---")
    profile.append_symbols = ask_yes_no("Append common special characters (e.g., @, !, #, $) to the end? (Y/n): ", default='y')
    profile.append_numbers = ask_yes_no("Append common random numbers (e.g., 1, 123, 2023) to the end? (Y/n): ", default='y')
    profile.use_separators = ask_yes_no("Insert common separators (_, -, ., @, #, $) between combined words? (Y/n): ", default='y')
    try:
        profile.min_len = int(ask_string("Minimum password length (default 6): ") or "6")
    except ValueError:
        profile.min_len = 6
    try:
        profile.max_len = int(ask_string("Maximum password length (default 16): ") or "16")
    except ValueError:
        profile.max_len = 16
    profile.min_len = max(1, profile.min_len)
    profile.max_len = max(profile.min_len, profile.max_len)

    return profile

# ----------------------------------------------------------------------
# Wordlist Generator
# ----------------------------------------------------------------------
class WordlistGenerator:
    """Generates wordlist from a Profile."""
    def __init__(self, profile):
        self.profile = profile
        self.words = set()
        self.suffixes = self._build_suffixes()
        self.min_source_len = self._get_min_source_len()

    def _build_suffixes(self):
        """Build the suffix list once so generation can respect final length limits."""
        suffixes = []
        if self.profile.append_symbols:
            suffixes.extend(SYMBOLS)
        if self.profile.append_numbers:
            suffixes.extend(NUMBERS)
        return suffixes

    def _get_min_source_len(self):
        """Allow shorter base words only when suffixes could bring them into range."""
        if not self.suffixes:
            return self.profile.min_len
        max_suffix_len = max(len(suffix) for suffix in self.suffixes)
        return max(1, self.profile.min_len - max_suffix_len)

    def _store_word(self, word):
        """Store a word only if it can still fit the requested final length range."""
        if self.min_source_len <= len(word) <= self.profile.max_len:
            self.words.add(word)

    def _store_variations(self, word):
        """Store case variations for words that are viable for the requested range."""
        if not word:
            return
        for variation in case_variations(word):
            self._store_word(variation)

    def add_leet_variations(self):
        """For every string in every tag, add its leet version if different."""
        new_entries = defaultdict(list)
        for tag, values in self.profile.data.items():
            for val in values:
                leet_val = leet_transform(val)
                if leet_val != val and leet_val not in values:
                    new_entries[tag].append(leet_val)
        for tag, vals in new_entries.items():
            self.profile.data[tag].extend(vals)

    def generate_single_words(self):
        """Generate case variations for all strings in all tags."""
        for values in self.profile.data.values():
            for val in values:
                self._store_variations(val)

    def generate_combinations(self):
        """
        Generate combinations of 2 or 3 tags.
        For each combination, generate all permutations of the tags,
        and for each product, optionally insert separators.
        """
        # Define which tags are eligible for combination.
        # We use all tags that have data, but exclude very specific date parts
        # to avoid too many combinations. Instead, we use the combined date strings.
        eligible_tags = [tag for tag, vals in self.profile.data.items() if vals]
        # Remove fine‑grained date tags, keep only the combined ones
        exclude_tags = {'birth_day', 'birth_month', 'partner_birth_day', 'partner_birth_month',
                        'anniversary_day', 'anniversary_month'}
        eligible_tags = [t for t in eligible_tags if t not in exclude_tags]

        # Build list of tag groups to combine.
        # We'll generate all pairs and all triples of eligible tags.
        # But to keep the number manageable, we skip combinations of only date parts.
        combos_to_try = []
        # Pairs
        for i, tag1 in enumerate(eligible_tags):
            for tag2 in eligible_tags[i+1:]:
                # Avoid combining two things that are essentially the same type? Not necessary.
                combos_to_try.append((tag1, tag2))
        # Triples
        for i, tag1 in enumerate(eligible_tags):
            for j, tag2 in enumerate(eligible_tags[i+1:], start=i+1):
                for tag3 in eligible_tags[j+1:]:
                    combos_to_try.append((tag1, tag2, tag3))

        # Limit to a reasonable number of combinations (e.g., first 500)
        # to prevent explosion. User can be warned if too many.
        if len(combos_to_try) > 500:
            print(f"Warning: {len(combos_to_try)} possible tag combinations. Limiting to first 500.")
            combos_to_try = combos_to_try[:500]

        total_combos = len(combos_to_try)
        print(f"\nGenerating combinations from {total_combos} tag sets...")

        # Prepare separators list
        separators = SEPARATORS if self.profile.use_separators else ['']

        for idx, tags in enumerate(combos_to_try, 1):
            # Progress indicator
            print(f"  Processing combination {idx}/{total_combos}...", end='\r')

            # Get lists for each tag
            lists = [self.profile.data[t] for t in tags]
            # Cartesian product
            for product in itertools.product(*lists):
                # For each permutation of the tags
                for perm_tags in itertools.permutations(tags):
                    # Reorder product according to permutation
                    perm_product = [product[tags.index(t)] for t in perm_tags]
                    # For each separator (including none)
                    for sep in separators:
                        combined = sep.join(perm_product)
                        if combined:
                            self._store_variations(combined)
        print()  # newline after progress

    def apply_suffixes(self):
        """Append symbol and/or number suffixes to each word."""
        if not self.suffixes:
            return
        new_words = set()
        for word in self.words:
            for suffix in self.suffixes:
                candidate = word + suffix
                if self.profile.min_len <= len(candidate) <= self.profile.max_len:
                    new_words.add(candidate)
        self.words.update(new_words)

    def filter_by_length(self):
        """Remove words outside min/max length."""
        self.words = {w for w in self.words
                      if self.profile.min_len <= len(w) <= self.profile.max_len}

    def generate(self):
        """Main generation pipeline."""
        print("\nStarting wordlist generation...")

        # Step 1: Add leet variations to profile
        print("Adding leet variations...")
        self.add_leet_variations()

        # Step 2: Single words with case
        print("Generating single word variations...")
        self.generate_single_words()
        print(f"  -> {len(self.words)} single words.")

        # Step 3: Combinations
        self.generate_combinations()
        print(f"  -> after combinations: {len(self.words)} words.")

        # Step 4: Suffixes
        if self.profile.append_symbols or self.profile.append_numbers:
            print("Applying suffixes...")
            self.apply_suffixes()
            print(f"  -> after suffixes: {len(self.words)} words.")

        # Step 5: Filter by length
        print("Filtering by length...")
        self.filter_by_length()
        print(f"  -> after length filter: {len(self.words)} words.")

        # Check for excessive size
        if len(self.words) > 10_000_000:
            print("\nWARNING: Wordlist exceeds 10 million entries. This may be very large.")
            proceed = ask_yes_no("Continue writing to file? (y/N): ", default='n')
            if not proceed:
                print("Aborted by user.")
                return False
        return True

    def write_to_file(self, filename="deep_profile_wordlist.txt"):
        """Write the wordlist shortest-to-longest, one word per line."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                words_by_length = defaultdict(list)
                for word in self.words:
                    words_by_length[len(word)].append(word)

                for length in range(self.profile.min_len, self.profile.max_len + 1):
                    for word in sorted(words_by_length.get(length, []), key=lambda value: (value.lower(), value)):
                        f.write(word + '\n')
        except IOError as e:
            print(f"Error writing file: {e}")
            return False
        return True

# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    # Collect data
    profile = run_questionnaire()

    # Check if we have any data
    if not profile.any_data():
        print("\nNo data entered. Exiting.")
        return

    # Show summary and confirm
    profile.display_summary()
    proceed = ask_yes_no("\nProceed with wordlist generation? (Y/n): ", default='y')
    if not proceed:
        print("Exiting.")
        return

    # Generate wordlist
    generator = WordlistGenerator(profile)
    if not generator.generate():
        return

    # Write to file
    output_file = "deep_profile_wordlist.txt"
    print(f"\nWriting to {output_file}...")
    if generator.write_to_file(output_file):
        # Print stats
        file_size = os.path.getsize(output_file) / (1024 * 1024)
        print(f"\nDone! Generated {len(generator.words)} unique words.")
        print(f"Output file: {output_file} ({file_size:.2f} MB)")
    else:
        print("Failed to write file.")

if __name__ == "__main__":
    main()
