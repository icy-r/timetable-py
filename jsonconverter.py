from bs4 import BeautifulSoup
import json


def parse_html_tables(html):
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all('table')  # Find all tables in the HTML
    timetables = []  # Store all extracted timetables

    for table in tables:
        # Table headers # Grp Id & Days
        thead = table.find('thead')
        header_rows = thead.find_all('tr') if thead else table.find_all('tr')[:2]

        if len(header_rows) < 2:
            continue  # Skip tables without enough header rows

        # Extract day headers
        days = [th.text.strip() for th in header_rows[1].find_all('th')]

        timetable = []
        rowspan_tracker = {day: [] for day in days}  # Track span row data
        rowspan_counter = {day: 0 for day in days}  # Track span count

        tbody = table.find('tbody') or table  # Use <table> if <tbody> is missing
        for row in tbody.find_all('tr', recursive=False):
            if row.get('class') and 'foot' in row.get('class'):
                continue  # Skip footer rows

            cells = row.find_all(['th', 'td'], recursive=False)
            if not cells:
                continue

            time_slot = cells[0].text.strip()
            schedule = {}
            col_idx = 0

            for i, day in enumerate(days):
                if len(cells) <= 1:
                    continue

                # Check for rowspan carryover
                if rowspan_counter[day] > 0:
                    schedule[day] = rowspan_tracker[day]
                    rowspan_counter[day] -= 1
                    continue

                if col_idx >= len(cells) - 1:  # Avoid out-of-bounds errors
                    continue

                cell = cells[col_idx + 1]  # Skip first column (time)
                rowspan = int(cell.get('rowspan', 1))  # Default to 1 if no rowspan
                content = []

                # Extract detailed nested table data
                nested_table = cell.find('table', class_='detailed')
                if nested_table:
                    content = [
                        " | ".join(td.text.strip() for td in sub_row.find_all('td'))
                        for sub_row in nested_table.find_all('tr')
                    ]
                else:
                    content.append(cell.text.strip())

                schedule[day] = content

                # Handle row spanning
                if rowspan > 1:
                    rowspan_tracker[day] = content
                    rowspan_counter[day] = rowspan - 1

                col_idx += 1

            if schedule:
                timetable.append({"time": time_slot, "schedule": schedule})

        if timetable:
            timetables.append(timetable)

    return timetables


# Load HTML
html_file_path = "timetable.html"
with open(html_file_path, "r", encoding="utf-8") as file:
    html_content = file.read()

json_output = parse_html_tables(html_content)

# Write JSON output
with open('timetables.json', "w", encoding="utf-8") as json_file:
    json.dump(json_output, json_file, ensure_ascii=False, indent=4)

