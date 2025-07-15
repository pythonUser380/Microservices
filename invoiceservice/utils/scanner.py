# shared/scanner.py

from shared.ReadImage import processImageText
from shared.utils.date_utils import convert_date
import pandas as pd

class ImageScanner:
    def __init__(self, image_path, filename, text, month, year):
        self.image_path = image_path
        self.filename = filename
        self.text = text
        self.month = month
        self.year = year
        self.data_frame = pd.DataFrame()

    def get_text(self):
        if not self.text:
            self.text = processImageText(self.image_path)
        return self.text

    def get_grocery_bill(self):
        # Placeholder logic – real version should parse the text into structured rows
        lines = self.text.split('\n')
        items = []
        for line in lines:
            parts = line.split()
            if len(parts) >= 3:
                try:
                    item = ' '.join(parts[:-2])
                    quantity = int(parts[-2])
                    price = float(parts[-1].replace(',', '.'))
                    items.append({'item': item, 'quantity': quantity, 'price': price})
                except:
                    continue
        self.data_frame = pd.DataFrame(items)

    def create_data_frame(self):
        if self.data_frame.empty:
            self.get_grocery_bill()
        return self.data_frame
