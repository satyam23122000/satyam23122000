import glob
import pandas as pd
from ftfy import fix_text
from unidecode import unidecode
import re
from datetime import datetime
from rapidfuzz import fuzz
from fuzzywuzzy import fuzz
import shutil
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
from faker import Faker
import threading
import time
import random
import pandas as pd 
import spacy 
import phonetics
from transformers import pipeline

# # Load the pre-trained NER model and tokenizer
# ner_pipeline = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english", grouped_entities=True)
nlp = spacy.load("en_core_web_sm")

current_datetime = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
fake = Faker(["en_IN"])
pin_data = pd.read_csv("g:/Shared drives/vs_code/State_city_Pincode.csv")


# Define folders and their corresponding output files
RAW_FOLDERS = [
    "G:/Shared drives/LLM/LLM_Raw/",
    "G:/Shared drives/TATA/tata_raw/",
    "G:/Shared drives/feature_testing/raw/",
    "G:/Shared drives/Bolero/Bolero_raw_Data/",
    "G:/Shared drives/Cruzio/Cruzio_Raw_Data/",
    "G:/Shared drives/Supro/Raw_Data/",
    "G:/Shared drives/MTB/Mahindra_Raw/",
    "g:/Shared drives/Veero/Raw_Data",
    "G:/Shared drives/Euler/Euler_Raw/",
    "g:/Shared drives/OSP/OSP_Raw/",
    "G:/Shared drives/Montra/Montra_raw_Data",
    "G:/Shared drives/store/Store_raw_Data"
]
OUTPUT_FILES = [
    f'G:/Shared drives/LLM/LLM_Combine/LLM_combine_{current_datetime}.csv',
    f'G:/Shared drives/TATA/Tata_combined/tata_combine_{current_datetime}.csv',
    f'G:/Shared drives/feature_testing/combine/test_combine_{current_datetime}.csv',
    f'G:/Shared drives/Bolero/Bolero_Combine/Bolero_combine_{current_datetime}.csv',
    f'G:/Shared drives/Cruzio/Cruzio_Combine/Cruzio_combine_{current_datetime}.csv',
    f'G:/Shared drives/Supro/Supro_Combine/Supro_combine_{current_datetime}.csv',
    f'G:/Shared drives/MTB/Mahindra_Combine/MTB_combine_{current_datetime}.csv',
    f'G:/Shared drives/Veero/Veero_Combine/Veero_combine_{current_datetime}.csv',
    f'G:/Shared drives/Euler/Euler_Combine/Euler_combine_{current_datetime}.csv',
    f'g:/Shared drives/OSP/OSP_Combine/OSP_Combine{current_datetime}.csv',
    f'G:/Shared drives/Montra/Montra_Combine/Montra_Combine{current_datetime}.csv',
    f'G:/Shared drives/store/Store_Combine{current_datetime}.csv'
]
CLEAN_OUTPUTS = [
    f'G:/Shared drives/LLM/Automated_clean/LLM_auto_clean_{current_datetime}.csv',
    f'G:/Shared drives/TATA/Tata_auto_clean/tata_auto_cleaned_{current_datetime}.csv',
    f'G:/Shared drives/feature_testing/auto_clean/test_auto_clean_{current_datetime}.csv',
    f'G:/Shared drives/Bolero/Bolero_Automated_clean/Bolero_auto_clean_{current_datetime}.csv',
    f'G:/Shared drives/Cruzio/Cruzio_Automated_clean/Cruzio_auto_clean_{current_datetime}.csv',
    f'G:/Shared drives/Supro/Automated_clean/Supro_auto_clean_{current_datetime}.csv',
    f'G:/Shared drives/MTB/Mahindra_Automated_clean/MTB_auto_clean_{current_datetime}.csv',
    f'g:/Shared drives/Veero/Automated_clean/Veero_auto_clean_{current_datetime}.csv',
    f'G:/Shared drives/Euler/Euler_Auto_clean/Euler_auto_clean_{current_datetime}.csv',
    f'g:/Shared drives/OSP/OSP_Auto_clean/OSP_auto_clean{current_datetime}.csv',
    f'G:/Shared drives/Montra/Montra_Automated_clean/Montra_Auto_clean{current_datetime}.Csv',
    f'G:/Shared drives/store/Store_Automated_clean{current_datetime}.Csv'
]
AUTO_DROPS = [
    f'G:/Shared drives/LLM/Auto_drop/LLM_auto_drop_{current_datetime}.csv',
    f'G:/Shared drives/TATA/Tata_auto_drop/tata_auto_drop_{current_datetime}.csv',
    f'G:/Shared drives/feature_testing/auto_drop/test_auto_drop_{current_datetime}.csv',
    f'G:/Shared drives/Bolero/Bolero_Auto_drop/Bolero_auto_drop_{current_datetime}.csv',
    f'G:/Shared drives/Cruzio/Cruzio_Auto_drop/Cruzio_auto_drop_{current_datetime}.csv',
    f'G:/Shared drives/Supro/Auto_drop/Supro_auto_drop_{current_datetime}.csv',
    f'G:/Shared drives/MTB/Mahindra_Auto_Drop/MTB_{current_datetime}.csv',
    f'g:/Shared drives/Veero/Auto_drop/Veero_Auto_drop_{current_datetime}.csv',
    f'G:/Shared drives/Euler/Euler_Auto_drop/Euler_Auto_drop_{current_datetime}.csv',
    f'g:/Shared drives/OSP/OSP_Auto_Drop/OSP_Auto_Drop_{current_datetime}.csv',
    f'G:/Shared drives/Montra/Montra_Auto_drop/Montra_Auto_Drop_{current_datetime}.csv',
    f'G:/Shared drives/store/Store_Auto_drop{current_datetime}.csv'
]
DUMP_FOLDERS = [
    "G:/Shared drives/LLM/LLM_dump/",
    "G:/Shared drives/TATA/Tata_dump/",
    "G:/Shared drives/feature_testing/dump/",
    "G:/Shared drives/Bolero/Bolero_Dump/",
    "G:/Shared drives/Cruzio/Cruzio_Dump/",
    "G:/Shared drives/Supro/Supro_Dump/",
    "G:/Shared drives/MTB/Mahindra_Dump/",
    "g:/Shared drives/Veero/Veero_Dump/",
    "G:/Shared drives/Euler/Euler_dump/",
    "g:/Shared drives/OSP/OSP_Dump/",
    "G:/Shared drives/Montra/Montra_Dump",
    "G:/Shared drives/store/Store_Dump"
]

# Ensure dump folders exist
for dump_folder in DUMP_FOLDERS:
    os.makedirs(dump_folder, exist_ok=True)


def process_csv_files(raw_folder, output_file, clean_output, auto_drop, dump_folder):
    """Process all CSV files in a specific raw folder."""

    # Get all CSV files
    csv_files = glob.glob(os.path.join(raw_folder, "*.csv"))
    dataframes = []
    for file in csv_files:
        df = pd.read_csv(file, encoding="utf-16", sep='\t', quotechar='"')
        dataframes.append(df)
    if not dataframes:
        print(f"No CSV files found in {raw_folder}.")
        return

    combined_df = pd.concat(dataframes, ignore_index=True)
    combined_df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"Combined CSV saved to: {output_file}")

    clean_df = pd.read_csv(output_file, low_memory=False)
    # Handle full name column
    if 'full name' in clean_df.columns:
        clean_df['full_name'] = clean_df['full_name'].fillna('') + ' ' + clean_df['full name'].fillna('')
        clean_df['full_name'] = clean_df['full_name'].str.strip()
        clean_df.drop(columns=['full name'], inplace=True)
    clean_df['full_name'] = clean_df['full_name'].apply(fix_text).apply(unidecode)
    clean_df['full_name'] = clean_df['full_name'].str.replace(r'[^a-zA-Z\s]', ' ', regex=True)
    clean_df["full_name"] = clean_df["full_name"].apply(clean_name)
    

    # Clean phone numbers
    phone_number_remove_list = ['p:\\+91', 'p:\\+1', 'p:', '\\+91', '91', '91+', '-', ' ']
    regex_pattern = '^(' + '|'.join(phone_number_remove_list) + ')'
    clean_df['phone_number'] = clean_df['phone_number'].str.replace(regex_pattern, '', regex=True)
    clean_df['Digit Count'] = clean_df['phone_number'].apply(lambda x: sum(c.isdigit() for c in str(x)))

    def modify_phone_number(phone_number):
        """Modify the phone number based on the specified conditions."""
        phone_number = str(phone_number)
        digit_count = sum(c.isdigit() for c in phone_number)
        
        # Ensure only numeric characters
        phone_number = ''.join(filter(str.isdigit, phone_number))

        if digit_count == 8:
            if phone_number[0] in ['9', '8', '7', '6']:
                phone_number += ''.join(random.choices('0123456789', k=2))
            else:
                phone_number = random.choice('9876') + random.choice('9876') + phone_number

        elif digit_count == 9:
            phone_number = random.choice('9876') + phone_number

        elif digit_count > 10:
            if phone_number[0] in ['9', '8', '7', '6']:
                phone_number = phone_number[:10]
            else:
                phone_number = random.choice('9876') + phone_number[:9]

        # Final adjustment for edge cases
        if len(phone_number) > 10:
            phone_number = phone_number[:10]
        return phone_number

    clean_df['phone_number'] = clean_df['phone_number'].apply(modify_phone_number)


    # Apply replacement map logic only if the file name contains 'LLM'
    if "LLM" in raw_folder.upper():
        replacement_map = {
            r'\btreo\s*passenger\s*electric\b': 'treo',
            r'\bjeeto\s*cng\b': 'jeeto-plus-cng',
            r'\bjeeto\s*petrol\b': 'jeeto-plus',
            r'\bjeeto\s*dsl\b': 'jeeto-plus-diesel',
            r'\bjeeto\b': 'jeeto-plus-diesel',
            r'\bzor\s*grand\b': 'zor-grand',
            r'\be\s*alfa\b': 'e-alfa-plus',
            r'\be\s*zeo\b': 'zeo'
        }
        clean_df['ad_name'] = clean_df['ad_name'].apply(
            lambda x: normalize_and_replace(x, replacement_map)
        )

    if "MTB" in raw_folder.upper():
        replacement_map = {
            r'\bFurio\s*11\b': 'furio-11',
            r'\bFurio\s*16\b': 'furio-16',
            r'\bFurio\s*17\b': 'furio-17',
            r'\bFurio\s*7\s*Cargo\b': 'furio-7-cargo',
            r'\bJayo\b': 'Jayo',
            r'\bX\s*28\b': 'blazo-x-28',
            r'\bX\s*55\b': 'blazo-x-55',
            r'\bFurio\s*7\s*Tipper\b':'Furio-7-tipper'
        }

        # Function to apply replacements
        def replace_text(text, replacements):
            for pattern, replacement in replacements.items():
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
            return text

        # Apply replacements to the 'ad_name' column
        clean_df['ad_name'] = clean_df['ad_name'].apply(lambda x: replace_text(str(x), replacement_map))


    if "TATA" in raw_folder.upper():
    # Replace 'ad_name' based on conditions in 'campaign_name'&'ad_name
        clean_df["ad_name"] = clean_df.apply(
            lambda row: "ace ev" if re.search(r"\bev\b", row["campaign_name"], re.IGNORECASE)
            else "ace ht" if re.search(r"\bace\b", row["campaign_name"], re.IGNORECASE) and row["ad_name"] != "ace ev"
            else "intra V70" if re.search(r"\bintra\b", row["campaign_name"], re.IGNORECASE)
            else "Yodha 1700" if re.search(r"\bYodha\s*\b", row["ad_name"], re.IGNORECASE)
            else "Winger School 1" if re.search(r'\bWinger\s*School\s*\b',row["ad_name"], re.IGNORECASE)
            else "Winger Tour" if re.search(r'\bWinger\s*Tour\s*\b',row["ad_name"], re.IGNORECASE)
            else "starbus" if re.search(r"\bCNG\s*STARBUS\s*\b",row["ad_name"], re.IGNORECASE)
            else "magic express school" if re.search(r"\bSchool\s*BUS\s*\b",row["ad_name"], re.IGNORECASE)
            else "magic express school" if re.search(r"\bMagic\s*School\s*\b",row["ad_name"], re.IGNORECASE)
            else "Signa 1918.k" if re.search(r"\bSigna\s*1918.k\b",row["ad_name"], re.IGNORECASE)
            else "magic route" if re.search(r"\bMagic\s*Route\b",row["ad_name"], re.IGNORECASE)
            else "Magic Bi-fuel" if re.search(r"\bMagic\b",row["ad_name"])
            else row["ad_name"],
            axis=1
        )
    # Save cleaned data
    clean_df.to_csv(clean_output, index=False, encoding="utf-8-sig")
    print(f"Cleaned CSV saved to: {clean_output}")

    clean_df['conditional_question_2'] = clean_df['conditional_question_2'].str.lower()
    pin_data['City'] = pin_data['City'].str.lower()
    clean_df = pd.merge(clean_df, pin_data, how='left', left_on='conditional_question_2', right_on='City')
    clean_df['Name_C'] = clean_df['full_name'].apply(lambda x: len(str(x).strip()))
    clean_df['full_name'] = clean_df.apply(lambda row: fake.name() if row['Name_C'] in [0,1,2] else row['full_name'], axis=1)
    clean_df = clean_df[clean_df['Digit Count'] >= 8]
    clean_df['word_c'] = clean_df['full_name'].apply(lambda x: len(str(x).split()))
    clean_df['full_name'] = clean_df['full_name'].apply(lambda x: str(x)[:30] if len(str(x)) > 30 else x)
    clean_df = clean_df.drop(['State','City','lead_status','Name_C','Digit Count'],axis=1)
    docs = list(nlp.pipe(clean_df['full_name'], disable=["parser"]))# Use nlp.pipe() for batch processing
    clean_df['full_name'] = [" ".join([token.text for token in doc if not token.is_stop]) for doc in docs]
    clean_df['ner'] = [[(ent.text, ent.label_) for ent in doc.ents] for doc in docs]
    # def process_batches(names, batch_size=32):
    #     """
    #     Process names in batches using the NER pipeline.

    #     Args:
    #         names (list): List of names to process.
    #         batch_size (int): Number of names to process in each batch.

    #     Returns:
    #         list: NER results for all names.
    #     """
    #     results = []
    #     for i in range(0, len(names), batch_size):
    #         batch = names[i:i + batch_size]
    #         try:
    #             batch_results = ner_pipeline(batch)
    #             results.extend(batch_results)
    #         except Exception as e:
    #             print(f"Error processing batch {i//batch_size + 1}: {e}")
    #             # Add placeholder for failed batches
    #             results.extend([[]] * len(batch))
    #     return results

    # # Ensure 'full_name' column exists
    # if 'full_name' in clean_df.columns:
    #     # Sample dataset
    #     names = clean_df['full_name'].dropna().tolist()

    #     # Process NER in batches
    #     ner_results = process_batches(names)

    #     # Simplify results to only include 'entity_group' and 'word'
    #     simplified_results = [
    #         [{'entity_group': item['entity_group'], 'word': item['word']} for item in result]
    #         for result in ner_results
    #     ]

    #     # Add results to DataFrame
    #     clean_df['NER'] = pd.Series(simplified_results)
    # else:
    #     print("The 'full_name' column does not exist in the DataFrame.")
    clean_df.to_csv(auto_drop, index=False, encoding='utf-8-sig')
    print(f"Dropped CSV saved to: {auto_drop}")

    for file in csv_files:
        shutil.move(file, dump_folder)
    print(f"Moved {len(csv_files)} files to {dump_folder} on {current_datetime}")



def clean_name(name):
    # Step 1: Remove excessive spaces and redundant letters
    name = re.sub(r'(?<=\b)([a-zA-Z])(?:\s+)(?=[a-zA-Z]\b)', r'\1', name)  # Remove single-character spaces
    name = re.sub(r'(.)\1{2,}', r'\1\1', name)  # Replace more than 2 consecutive repeating characters

    # Step 2: Normalize case and split into words
    name = name.lower().strip()  # Ensure uniform casing for processing
    words = name.split()

    # Step 3: Remove duplicates using phonetic and fuzzy matching
    cleaned_words = []
    for word in words:
        # Generate phonetic code for the word
        word_phonetic = phonetics.dmetaphone(word)[0]  # Get the first phonetic code
        
        # Check against existing cleaned words
        if not any(
            (fuzz.ratio(word, existing_word) > 85) or 
            (word_phonetic == phonetics.dmetaphone(existing_word)[0])
            for existing_word in cleaned_words
        ):
            cleaned_words.append(word)

    # Step 4: Combine cleaned words and format title case
    cleaned_name = " ".join(cleaned_words).title()
    return cleaned_name


def normalize_and_replace(ad_name, replacement_map):
    ad_name = ad_name.lower()
    ad_name = re.sub(r'[^a-z0-9\s]', '', ad_name)
    ad_name = re.sub(r'\s+', ' ', ad_name).strip()
    for pattern, replacement in replacement_map.items():
        if re.search(pattern, ad_name):
            return replacement
    return ad_name


class CsvEventHandler(FileSystemEventHandler):
    """Event handler for folder monitoring with a delay and file stability check."""
    
    def is_file_stable(self, file_path, check_interval=2, stable_time=10):
        """
        Check if the file is stable (not being written to) for a specified time.
        Args:
            file_path (str): Path of the file to check.
            check_interval (int): Interval in seconds between size checks.
            stable_time (int): Time in seconds the file size must remain constant.
        Returns:
            bool: True if the file is stable, False otherwise.
        """
        last_size = -1
        stable_duration = 0

        while stable_duration < stable_time:
            try:
                current_size = os.path.getsize(file_path)
            except OSError:
                # File might not exist yet, or an error occurred while accessing it.
                return False
            
            if current_size == last_size:
                stable_duration += check_interval
            else:
                stable_duration = 0  # Reset if the file size changes
            
            last_size = current_size
            time.sleep(check_interval)
        
        return True

    def on_created(self, event):
        if event.src_path.endswith(".csv"):
            print(f"New file detected: {event.src_path}")
            
            for i, raw_folder in enumerate(RAW_FOLDERS):
                if raw_folder in event.src_path:
                    print(f"Checking stability for {event.src_path}...")
                    threading.Thread(
                        target=self.process_after_stability_check,
                        args=(event.src_path, i)
                    ).start()
                    break

    def process_after_stability_check(self, file_path, index):
        if self.is_file_stable(file_path):
            print(f"File {file_path} is stable. Waiting 30 seconds before processing.")
            time.sleep(30)  # Adding 30-second delay
            
            print(f"File {file_path} is stable. Scheduling processing.")
            threading.Timer(
                20, 
                process_csv_files, 
                args=(RAW_FOLDERS[index], OUTPUT_FILES[index], CLEAN_OUTPUTS[index], AUTO_DROPS[index], DUMP_FOLDERS[index])
            ).start()
        else:
            print(f"File {file_path} is not stable. Skipping processing.")
        
        return True

    def on_created(self, event):
        if event.src_path.endswith(".csv"):
            print(f"New file detected: {event.src_path}")
            
            for i, raw_folder in enumerate(RAW_FOLDERS):
                if raw_folder in event.src_path:
                    print(f"Checking stability for {event.src_path}...")
                    threading.Thread(
                        target=self.process_after_stability_check,
                        args=(event.src_path, i)
                    ).start()
                    break

    def process_after_stability_check(self, file_path, index):
        if self.is_file_stable(file_path):
            print(f"File {file_path} is stable. Scheduling processing.")
            threading.Timer(
                20, 
                process_csv_files, 
                args=(RAW_FOLDERS[index], OUTPUT_FILES[index], CLEAN_OUTPUTS[index], AUTO_DROPS[index], DUMP_FOLDERS[index])
            ).start()
        else:
            print(f"File {file_path} is not stable. Skipping processing.")

if __name__ == "__main__":
    event_handler = CsvEventHandler()
    observer = Observer()
    for raw_folder in RAW_FOLDERS:
        observer.schedule(event_handler, raw_folder, recursive=False)
    observer.start()
    print(f"Monitoring folders: {RAW_FOLDERS}")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
