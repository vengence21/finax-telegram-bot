class EntryData:
    def __init__(self, row):
        if len(row) < 5:
            raise ValueError("Incomplete data returned from database.")

        self.four_digits_id = row[0]
        self.entry = row[1]
        self.entry_size = row[2]
        self.multiplier = row[3]
        self.added_on = row[4]

    def __repr__(self):
        amount = 0.8 if self.entry_size == 'b' else 0.7
        total_amount = amount * self.multiplier

        return f"Entry: {self.entry}; Amount: {total_amount:.2f}; Time: {self.added_on.strftime('%d/%m/%Y %H:%M:%S')}"
