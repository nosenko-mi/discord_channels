import sys
import pandas as pd
import emoji

def filter_relevant(content):
    if isinstance(content, str) and len(content) > 20:  # Exclude very short messages like "Hi"
        return True
    return False

input = sys.argv[1]
output = sys.argv[2]


df = pd.read_csv(input)
df_cleaned = df.dropna(subset=['Content'])
df_cleaned.loc[:, 'Content'] = df_cleaned['Content'].str.replace('\n', ' ', regex=False)
df_cleaned['Group'] = (df_cleaned['AuthorID'] != df_cleaned['AuthorID'].shift()).cumsum()

df_combined = df_cleaned.groupby(['Group', 'AuthorID'], as_index=False).agg({
    'Author': 'first',       # Keep the first Author
    'Content': '. '.join,   # Combine 'Content'
    'Date': 'first',        # Keep the first Date in each group
})
df_combined = df_combined.drop(columns=['Group'])
df_combined['Content'] = df_combined['Content'].apply(lambda text: emoji.demojize(text))



data_filtered = df_combined[df_combined['Content'].apply(filter_relevant)]

data_filtered['Date'] = pd.to_datetime(data_filtered['Date'])
data = data_filtered.sort_values(by='Date')

threads = []
current_thread = []
for _, row in data.iterrows():
    if current_thread and (row['Date'] - current_thread[-1]['Date']).total_seconds() > 300:
        threads.append(current_thread)
        current_thread = []
    current_thread.append(row)
if current_thread:
    threads.append(current_thread)


qa_pairs = []

for thread in threads:
    question = None
    answer = []
    for message in thread:
        if '?' in message['Content']:  # Identify a question
            if question:  # If we already have a question, finalize the previous Q&A pair
                qa_pairs.append({'Question': question, 'Answer': ' '.join(answer)})
                answer = []
            question = message['Content']
        else:
            answer.append(message['Content'])

    # Append the last Q&A pair
    if question:
        qa_pairs.append({'Question': question, 'Answer': ' '.join(answer)})

valid_qa_pairs = []
for p in qa_pairs:
    if p['Question'] != '' and p['Answer'] != '':
        valid_qa_pairs.append(p)


qa_df = pd.DataFrame(valid_qa_pairs)
qa_df.to_csv(output, index=False)

# How to run:
# python prepare.py "path/to/raw/csv/from/discordloader/file.csv" "help-qa-2.csv"