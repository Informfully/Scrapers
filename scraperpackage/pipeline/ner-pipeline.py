import pandas as pd
import stanza
import os

# Check if English model exists and download if it is not yet installed
# stanza.download('en')

# Define file folder
DIR = r'./jsondata'

# Instantiate the model
NLP = stanza.Pipeline(lang = 'en', processors = 'tokenize, ner')

def perform_ner():

    currentFileIndex = 0
    directorySize = len(os.listdir(DIR))

    for filename in os.listdir(DIR):

        path = DIR + '/' + filename
        filenameAlt = path[0:-5] + '_NER.json'

        df = pd.read_json(path, orient = 'index')
        df['entity'] = ''

        # Perform NER with Stanza library
        for i, row in df.iterrows():
            doc = NLP(row['tweet'])
            entities = []

            for ent in doc.ents:
                if ent.type == "ORG":
                    entities.append(ent.text)

            df.at[i, 'entity'] = entities

        # Create a copy of the input file and append the results to the end
        currentFileIndex += 1
        print('File ' + filename + ' has been processed.')
        print('Step ' + str(currentFileIndex) + ' of ' + str(directorySize) + ' completed.')
        df.to_json(path_or_buf = filenameAlt, orient = 'index')

def main():
    print('Starting NER...\n')
    perform_ner()
    print('Process completed!')

main()
