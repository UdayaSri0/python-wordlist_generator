#!/usr/bin/env python3
"""
Deep User Profiling Wordlist Generator
Generates a custom wordlist based on personal information provided by the user.
"""

import itertools
import os
import sys
from collections import defaultdict

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
# Common symbols to append if enabled
SYMBOLS = ['!', '@', '#', '$', '%', '^', '&', '*', '?', '.']

# Common number suffixes to append if enabled
NUMBERS = [
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    '00', '11', '22', '33', '44', '55', '66', '77', '88', '99',
    '123', '1234', '2020', '2021', '2022', '2023', '2024', '2025'
]

# Leet mapping (case-insensitive, but we apply to original case)
LEET_MAP = {
    'a': '@', 'A': '@',
    'e': '3', 'E': '3',
    'i': '1', 'I': '1',
    'o': '0', 'O': '0',
    's': '$', 'S': '$'
}

# Combination rules: each rule is a list of tags to combine.
# For each rule, all permutations of the tags will be generated.
RULES = [
    ['first_name', 'last_name'],
    ['first_name', 'last_name', 'birth_year'],
    ['first_name', 'birth_year'],
    ['last_name', 'birth_year'],
    ['nickname', 'birth_year'],
    ['partner_name', 'birth_year'],
    ['child_name', 'birth_year'],
    ['pet_name', 'birth_year'],
    ['first_name', 'pet_name'],
    ['first_name', 'child_name'],
    ['first_name', 'partner_name'],
    ['school', 'birth_year'],
    ['company', 'birth_year'],
    ['first_name', 'school'],
    ['last_name', 'school'],
    ['first_name', 'company'],
    ['last_name', 'company'],
    ['first_name', 'last_name', 'school'],
    ['first_name', 'last_name', 'company'],
    ['first_name', 'city'],
    ['last_name', 'city'],
    ['first_name', 'street'],
    ['last_name', 'street'],
    ['first_name', 'sports_team'],
    ['last_name', 'sports_team'],
    ['first_name', 'color'],
    ['last_name', 'color'],
    ['first_name', 'band'],
    ['last_name', 'band'],
    ['first_name', 'movie'],
    ['last_name', 'movie'],
    ['first_name', 'car'],
    ['last_name', 'car'],
    ['birth_year', 'phone'],
    ['birth_year', 'zip'],
    ['first_name', 'phone'],
    ['last_name', 'phone'],
    ['first_name', 'lucky_number'],
    ['last_name', 'lucky_number'],
    ['nickname', 'lucky_number'],
    ['first_name', 'birth_date_combo'],
    ['last_name', 'birth_date_combo'],
    ['birth_year', 'birth_date_combo'],
]

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def leet_transform(word):
    """Apply basic leet substitution to a word."""
    if not word:
        return word
    result = []
    for ch in word:
        result.append(LEET_MAP.get(ch, ch))
    return ''.join(result)

def case_variations(word):
    """Return a set of common case variations for a word."""
    vars_set = set()
    vars_set.add(word)                     # original
    vars_set.add(word.lower())              # lowercase
    vars_set.add(word.upper())              # uppercase
    vars_set.add(word.title())               # title case
    vars_set.add(word.swapcase())            # inverted case
    # Remove any empty strings
    vars_set.discard('')
    return vars_set

def process_dob(day, month, year):
    """
    Given day, month, year strings (may be empty), return a dictionary
    of tags to list of values for DOB related entries.
    """
    results = defaultdict(list)
    if day:
        day = day.zfill(2)
        results['birth_day'].append(day)
    if month:
        month = month.zfill(2)
        results['birth_month'].append(month)
    if year:
        year_full = year.zfill(4) if len(year) <= 4 else year
        results['birth_year'].append(year_full)
        if len(year_full) == 4:
            results['birth_year'].append(year_full[2:])  # two-digit year
    # Combined forms (only if both day and month, or all three)
    if day and month:
        results['birth_date_combo'].append(day + month)      # DDMM
        results['birth_date_combo'].append(month + day)      # MMDD
        if year:
            results['birth_date_combo'].append(day + month + year_full)  # DDMMYYYY
    return results

def ask_string(prompt):
    """Ask for a single string, return stripped value or None if empty."""
    val = input(prompt).strip()
    return val if val else None

def ask_multiple(prompt):
    """Ask for comma-separated values, return list of stripped non-empty strings."""
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

def ask_dob(prompt_prefix):
    """Ask for day, month, year and return processed DOB dict."""
    print(f"\n{prompt_prefix} (press Enter to skip any field)")
    day = ask_string("  Day (DD): ")
    month = ask_string("  Month (MM): ")
    year = ask_string("  Year (YYYY): ")
    return process_dob(day, month, year)

# ----------------------------------------------------------------------
# Questionnaire
# ----------------------------------------------------------------------
def collect_user_data():
    """
    Run the interactive questionnaire and return a dictionary
    mapping tags to lists of strings.
    """
    data = defaultdict(list)

    print("\n" + "="*60)
    print("DEEP USER PROFILING WORDLIST GENERATOR")
    print("="*60)
    print("Enter information about the target. Press Enter to skip any field.")
    print("For multiple entries (e.g., pets), separate with commas.\n")

    # Personal Info
    print("\n--- PERSONAL INFO ---")
    first = ask_string("First Name: ")
    if first:
        data['first_name'].append(first)
    middle = ask_string("Middle Name: ")
    if middle:
        data['middle_name'].append(middle)
    last = ask_string("Last Name: ")
    if last:
        data['last_name'].append(last)
    nick = ask_string("Nickname: ")
    if nick:
        data['nickname'].append(nick)

    # Date of Birth
    dob_data = ask_dob("Date of Birth")
    for tag, values in dob_data.items():
        data[tag].extend(values)

    # Family & Relationships
    print("\n--- FAMILY & RELATIONSHIPS ---")
    partner = ask_string("Partner's Name: ")
    if partner:
        data['partner_name'].append(partner)
    partner_nick = ask_string("Partner's Nickname: ")
    if partner_nick:
        data['partner_nickname'].append(partner_nick)
    partner_dob = ask_dob("Partner's Date of Birth")
    for tag, values in partner_dob.items():
        # Rename tags to partner_*
        if tag.startswith('birth_'):
            new_tag = 'partner_' + tag
        else:
            new_tag = 'partner_' + tag
        data[new_tag].extend(values)

    children = ask_multiple("Child(ren)'s Name(s) (comma separated): ")
    if children:
        data['child_name'].extend(children)
    child_nicks = ask_multiple("Child(ren)'s Nickname(s): ")
    if child_nicks:
        data['child_nickname'].extend(child_nicks)
    # We skip child DOB for simplicity, but you could add similar logic

    parents = ask_multiple("Parent(s)' Name(s): ")
    if parents:
        data['parent_name'].extend(parents)

    pets = ask_multiple("Pet(s)' Name(s): ")
    if pets:
        data['pet_name'].extend(pets)

    # Education & Career
    print("\n--- EDUCATION & CAREER ---")
    company = ask_string("Company/Workspace Name: ")
    if company:
        data['company'].append(company)
    school = ask_string("School Name: ")
    if school:
        data['school'].append(school)
    campus = ask_string("Campus Name: ")
    if campus:
        data['campus'].append(campus)
    uni = ask_string("University: ")
    if uni:
        data['university'].append(uni)
    teacher = ask_string("Favorite/Memorable Teacher's Name: ")
    if teacher:
        data['teacher'].append(teacher)

    # Interests & Geography
    print("\n--- INTERESTS & GEOGRAPHY ---")
    hometown = ask_string("Hometown: ")
    if hometown:
        data['hometown'].append(hometown)
    city = ask_string("Current City: ")
    if city:
        data['city'].append(city)
    street = ask_string("Street Name: ")
    if street:
        data['street'].append(street)
    sports = ask_string("Favorite Sports Team: ")
    if sports:
        data['sports_team'].append(sports)
    color = ask_string("Favorite Color: ")
    if color:
        data['color'].append(color)
    band = ask_string("Favorite Band/Artist: ")
    if band:
        data['band'].append(band)
    movie = ask_string("Favorite Movie/Character: ")
    if movie:
        data['movie'].append(movie)
    car = ask_string("Car Brand/Model: ")
    if car:
        data['car'].append(car)

    # Numbers & IDs
    print("\n--- NUMBERS & IDs ---")
    phones = ask_multiple("Phone Number(s): ")
    if phones:
        data['phone'].extend(phones)
    ids = ask_multiple("Important ID Numbers (e.g., student/employee ID): ")
    if ids:
        data['id_number'].extend(ids)
    zipcode = ask_string("Postal/Zip Code: ")
    if zipcode:
        data['zip'].append(zipcode)
    lucky = ask_multiple("Personal 'Lucky' Numbers: ")
    if lucky:
        data['lucky_number'].extend(lucky)

    # Modifiers
    print("\n--- MODIFIERS ---")
    append_symbols = ask_yes_no("Append common special characters (e.g., @, !, #, $) to the end? (Y/n): ", default='y')
    append_numbers = ask_yes_no("Append common random numbers (e.g., 1, 123, 2023) to the end? (Y/n): ", default='y')
    try:
        min_len = int(ask_string("Minimum password length (default 6): ") or "6")
    except ValueError:
        min_len = 6
    try:
        max_len = int(ask_string("Maximum password length (default 16): ") or "16")
    except ValueError:
        max_len = 16

    return data, append_symbols, append_numbers, min_len, max_len

# ----------------------------------------------------------------------
# Wordlist generation
# ----------------------------------------------------------------------
def add_leet_variations(tagged_data):
    """For every string in every tag, add its leet version if different."""
    new_entries = defaultdict(list)
    for tag, values in tagged_data.items():
        for val in values:
            leet_val = leet_transform(val)
            if leet_val != val and leet_val not in values:
                new_entries[tag].append(leet_val)
    for tag, vals in new_entries.items():
        tagged_data[tag].extend(vals)

def generate_single_words(tagged_data):
    """Generate case variations for all strings in all tags."""
    words = set()
    for values in tagged_data.values():
        for val in values:
            words.update(case_variations(val))
    return words

def generate_combinations(tagged_data, rules):
    """
    Generate combined strings according to the rules.
    Returns a set of raw combined strings (no case variations yet).
    """
    combos = set()
    total_rules = len(rules)
    for idx, rule in enumerate(rules):
        # Print progress
        print(f"  Processing combination rule {idx+1}/{total_rules}...", end='\r')
        # Check if all tags in rule exist and are non-empty
        tag_lists = []
        for tag in rule:
            if tag not in tagged_data or not tagged_data[tag]:
                break
            tag_lists.append(tagged_data[tag])
        else:
            # All tags present
            # Generate all permutations of the tags (order matters)
            for perm in itertools.permutations(rule):
                # Get the lists in the permuted order
                lists = [tagged_data[t] for t in perm]
                # Cartesian product
                for combination in itertools.product(*lists):
                    combined = ''.join(combination)
                    combos.add(combined)
    print()  # newline after progress
    return combos

def apply_suffixes(words, symbols_enabled, numbers_enabled):
    """Append symbol and/or number suffixes to each word."""
    if not (symbols_enabled or numbers_enabled):
        return words
    new_words = set()
    suffixes = []
    if symbols_enabled:
        suffixes.extend(SYMBOLS)
    if numbers_enabled:
        suffixes.extend(NUMBERS)
    for word in words:
        for suffix in suffixes:
            new_words.add(word + suffix)
    return new_words

def filter_by_length(words, min_len, max_len):
    """Return only words with length between min_len and max_len inclusive."""
    return {w for w in words if min_len <= len(w) <= max_len}

# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    # Collect data
    tagged_data, symbols_enabled, numbers_enabled, min_len, max_len = collect_user_data()

    # Check if we have any data
    if not any(tagged_data.values()):
        print("\nNo data entered. Exiting.")
        return

    # Add leet versions
    print("\nAdding leet variations...")
    add_leet_variations(tagged_data)

    # Generate single words (case variations)
    print("Generating single word variations...")
    all_words = generate_single_words(tagged_data)
    print(f"  -> {len(all_words)} single words (with case).")

    # Generate combinations
    print("Generating combinations...")
    raw_combos = generate_combinations(tagged_data, RULES)
    print(f"  -> {len(raw_combos)} raw combinations.")

    # Apply case variations to combos
    print("Applying case variations to combinations...")
    combo_words = set()
    for combo in raw_combos:
        combo_words.update(case_variations(combo))
    print(f"  -> {len(combo_words)} combined words (with case).")

    # Merge
    all_words.update(combo_words)
    print(f"Total before suffixes: {len(all_words)}")

    # Apply suffixes
    if symbols_enabled or numbers_enabled:
        print("Applying suffixes...")
        all_words = apply_suffixes(all_words, symbols_enabled, numbers_enabled)
        print(f"  -> after suffixes: {len(all_words)}")

    # Filter by length
    print("Filtering by length...")
    all_words = filter_by_length(all_words, min_len, max_len)
    print(f"  -> after length filter: {len(all_words)}")

    # Write to file
    output_file = "deep_profile_wordlist.txt"
    print(f"Writing to {output_file}...")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for word in sorted(all_words):
                f.write(word + '\n')
    except IOError as e:
        print(f"Error writing file: {e}")
        return

    # Print stats
    file_size = os.path.getsize(output_file) / (1024 * 1024)
    print(f"\nDone! Generated {len(all_words)} unique words.")
    print(f"Output file: {output_file} ({file_size:.2f} MB)")

if __name__ == "__main__":
    main()