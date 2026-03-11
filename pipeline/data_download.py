import kagglehub
import os
import json

from pathlib import Path

def load_imdb_texts(dir: str):
    dir = Path(dir)
    texts, labels = [], []

    for label_name, y in [('pos', 1), ('neg', 0)]:
        folder = dir / label_name
        if not folder.exists():
            raise FileNotFoundError(f"Folder not found: {folder}")
        
        for fp in sorted(folder.glob('*.txt')):
            text = fp.read_text(encoding='utf-8', errors='ignore')
            text = text.replace('<br />', ' ').strip()
            texts.append(text)
            labels.append(y)

    return texts, labels

def save_data_json(X, y, path):
    data = {
        'X': X,
        'y': y
    }

    with open(path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)

if __name__ == '__main__':
    path = kagglehub.dataset_download("pawankumargunjan/imdb-review", output_dir='./data')

    DATA_ROOT = 'data/aclImdb'
    X_train, y_train = load_imdb_texts(os.path.join(DATA_ROOT, 'train'))
    X_test, y_test = load_imdb_texts(os.path.join(DATA_ROOT, 'test'))

    train_data_path = './data/train_data.json'
    save_data_json(X_train, y_train, train_data_path)

    test_data_path = './data/test_data.json'
    save_data_json(X_test, y_test, test_data_path)

    print(f"Train: {len(X_train)} docs, Test: {len(X_test)} docs")