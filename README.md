# Project Report: NLP Pipeline for Bechdel Test Analysis (First Step)

This project implements an NLP pipeline to analyze literary texts (novels) and determine if they pass the **first step** of the Bechdel-Wallace test: identifying whether the novel contains at least two named female characters.

## 1. Context

The Bechdel-Wallace test measures the representation of women in fiction. Its criteria are:
1. The work must have at least two named female characters.
2. Who talk to each other.
3. About something besides a man.

This pipeline focuses *only* on automating the first criterion.

## 2. Datasets Used

* **Primary Dataset:** Full text of novels sourced from Project Gutenberg.
    * *Dracula* by Bram Stoker
    * *Emma* by Jane Austen
    * *Pride and Prejudice* by Jane Austen
* **Evaluation Dataset:** Annotated books from the QuoteLi project ([https://muzny.github.io/quoteli.html](https://muzny.github.io/quoteli.html)) were used for ground truth character/gender information. Ground truth data was extracted from XML files (`emma_full.xml`, `steppe_full.xml`, `pp_full.xml`).
* **Additional Resources:** Custom-created lists of common male (`male_names.txt`) and female (`female_names.txt`) names (around 200 each) were used for rule-based gender classification.

## 3. Pipeline Design and Implementation

The pipeline consists of several stages implemented across different notebooks:

### 3.1 Text Preprocessing (`notebooks/00_pre_proc.ipynb`)

* **Objective:** Clean raw novel text from Project Gutenberg.
* **Methods:**
    * Remove Project Gutenberg headers/footers using regex.
    * Normalize different quotation mark styles.
    * Fix paragraph breaks resulting from hard-wrapped lines.
    * Remove illustration blocks.
* **Output:** Cleaned text file (e.g., `../data/dracula_cleaned.txt`, `../data/pp_cleaned.txt`).

### 3.2 Character Identification (`notebooks/01_character_identification.ipynb`)

* **Objective:** Identify character mentions and consolidate them into unique character representations.
* **Methods:**
    * **NER:** Used `compnet-renard/bert-base-cased-literary-NER` model via Hugging Face `transformers` pipeline to find 'PER' (Person) entities. Processed text in chunks due to model input size limits.
    * **Filtering:** Removed noise like standalone titles (Mr, Mrs, etc.) and punctuation-only mentions.
    * **Consolidation:**
        * Used the `nicknames` library to map variations (e.g., "lizzy") to canonical names (e.g., "elizabeth").
        * Applied rule-based fallback (stripping titles, lowercasing) for names not in the dictionary.
        * Generated a final `canonical_key` for each character group based on the most frequent variation.
* **Output:** Consolidated character list with mention counts and variations (e.g., `../data/character_analysis_consolidated_nicknames.csv`).

### 3.3 Gender Classification - Rule-Based (`notebooks/02_gender.ipynb`)

* **Objective:** Initial high-precision gender classification using explicit titles and name lists.
* **Methods:**
    * Checked `canonical_key` prefixes against predefined lists of male (`MALE_TITLES`) and female (`FEMALE_TITLES`) titles.
    * If no title match, checked the first name part against the loaded male/female name lists (`female_names.txt`, `male_names.txt`). Names in both lists were marked 'Unknown'.
    * Defaulted to 'Unknown' if no title or unique name list match was found.
* **Output:** Character list with initial `classified_gender` and `final_gender` columns (e.g., `../data/character_analysis_gendered_new.csv`).

### 3.4 Contextual Gender Analysis (`notebooks/02b_context.ipynb`)

* **Objective:** Refine gender classification for characters initially marked 'Unknown' using context.
* **Methods:**
    * **Pronoun Analysis:** Tokenized text into sentences (using NLTK). Analyzed sentences containing character mentions (including variations) for gendered pronouns (he/him/his, she/her/hers). Classified gender based on pronoun counts exceeding defined thresholds (`MIN_PRONOUN_THRESHOLD`, `MIN_PRONOUN_DIFFERENCE`).
    * **Coreference Resolution:** Used spaCy (`en_core_web_lg`) with the `coreferee` extension to process the text and identify coreference chains. Analyzed chains containing character mentions to aggregate gender evidence (from pronouns within the chain or known gendered mentions in the chain) to re-classify 'Unknown' characters.
* **Output:** Updated character list with contextually refined gender (`final_gender_contextual`) and coreference-based gender (`coref_gender`) (e.g., `../data/character_analysis_gendered_contextual_new.csv`, `../data/character_analysis_gendered_coref_new_1.csv`).

### 3.5 Evaluation (`notebooks/04_evaluations.ipynb`)

* **Objective:** Assess the performance of the gender classification against ground truth.
* **Methods:**
    * Loaded ground truth data derived from QuoteLi XML files.
    * Merged final pipeline results (`coref_gender` column from `character_analysis_gendered_coref_new_1.csv` for each novel) with ground truth based on `canonical_key` and `novel`.
    * Calculated standard classification metrics (Accuracy, Precision, Recall, F1-score) overall and per novel.
    * Generated confusion matrices.
* **Output:** Evaluation metrics and visualizations.

## 4. Evaluation Results

* **Overall Accuracy:** 95.00%
* **Weighted Avg F1-Score:** 92.59%
* **Macro Avg F1-Score:** 65.52% (Lower due to the small number of 'Unknown' examples in the ground truth test set)
* **Key Observation:** The system performed well, especially in distinguishing Male/Female. Misclassifications primarily involved the 'Unknown' category. 'Emma' was classified perfectly; 'Pride and Prejudice' had one 'Unknown' ground truth character misclassified as 'Female' by the pipeline.

## 5. Conclusions and Future Improvements

* **Findings:** The pipeline effectively identifies character gender for the first step of the Bechdel test with high overall accuracy. Contextual analysis improves coverage over purely rule-based methods.
* **Limitations:** Relies on pre-trained models, potential consolidation errors, assumes binary gender, performance may vary by genre.
* **Future Work:** Enhance character consolidation (fuzzy matching, relationships), improve gender classification models (custom training, non-binary options), implement the full Bechdel test (dialogue detection, topic modeling), improve scalability.