from bs4 import BeautifulSoup
import json

def extract_timetable_data_revised(html_file_path, output_json_path):
    """
    Extracts timetable data from an HTML file, correctly handling rowspan,
    and saves it to a JSON file.

    Args:
        html_file_path (str): Path to the input HTML file.
        output_json_path (str): Path to save the output JSON file.
    """

    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    timetable_data = []

    timetable_tables = soup.find_all('table', id=lambda x: x and x.startswith('table_'))

    for table in timetable_tables:
        group_name = table.caption.text.strip() if table.caption else "Unknown Group"
        table_id = table.get('id')
        group_timetable = {"group": group_name, "table_id": table_id, "schedule": {}}

        header_row = table.find('thead').find_all('tr')[1]
        days = [th.text.strip() for th in header_row.find_all('th', class_='xAxis')]

        body_rows = table.find('tbody').find_all('tr')

        time_slots = [] # To keep track of time slots in order
        schedule_data_grid = [] # 2D list to hold schedule data, rows are time slots, cols are days

        for row_index, row in enumerate(body_rows):
            time_slot_cell = row.find('th', class_='yAxis')
            if not time_slot_cell:
                continue
            time_slot = time_slot_cell.text.strip()
            time_slots.append(time_slot)
            schedule_row_data = []

            day_cells = row.find_all('td')
            col_index_offset = 0 # To handle rowspan cells correctly
            for day_index, day_cell in enumerate(day_cells):
                while col_index_offset > 0: # Skip columns spanned by previous rowspan cells
                    schedule_row_data.append(None) # Placeholder for spanned cells
                    col_index_offset -= 1

                cell_data = []
                rowspan = int(day_cell.get('rowspan', 1))
                detailed_table = day_cell.find('table', class_='detailed')

                if detailed_table:
                    for detailed_row in detailed_table.find_all('tr'):
                        detailed_data = [td.text.strip() for td in detailed_row.find_all('td', class_='detailed')]
                        cell_data.extend(detailed_data)
                elif day_cell.text.strip() and day_cell.text.strip() not in ('---', '-x-'):
                    cell_data = [day_cell.text.strip()]
                else:
                    cell_data = []

                schedule_row_data.append({'content': cell_data, 'rowspan': rowspan})
                col_index_offset = rowspan - 1

            schedule_data_grid.append(schedule_row_data)


        for time_slot_index, time_slot in enumerate(time_slots):
            group_timetable["schedule"][time_slot] = {}
            for day_index, day_name in enumerate(days):
                group_timetable["schedule"][time_slot][day_name] = []
                if time_slot_index < len(schedule_data_grid) and day_index < len(schedule_data_grid[time_slot_index]):
                    cell_info = schedule_data_grid[time_slot_index][day_index]
                else:
                    print(f"Warning: Index out of range for time_slot_index: {time_slot_index}, day_index: {day_index}")
                    cell_info = None  # Or handle accordingly
                if cell_info and cell_info['content']:
                    group_timetable["schedule"][time_slot][day_name].append(cell_info['content'])
                else:
                    group_timetable["schedule"][time_slot][day_name].append([]) # Empty slot


        timetable_data.append(group_timetable)


    with open(output_json_path, 'w', encoding='utf-8') as outfile:
        json.dump(timetable_data, outfile, indent=4, ensure_ascii=False)

# Example usage:
html_file = 'y3s1.html' # Replace with your file path
json_file = 'timetable_data_revised.json'
extract_timetable_data_revised(html_file, json_file)
print(f"Revised timetable data extracted and saved to {json_file}")