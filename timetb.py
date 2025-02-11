from bs4 import BeautifulSoup
import json

#new commit 
def parse_timetable_html_to_json(html_file_path):
    """
    
    Args:
        html_file_path (str): Path to the HTML file.

    Returns:
        str: JSON string representing the timetable data.
    """

    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    tables = soup.find_all('table')
    timetable_data = []

    for table in tables:
        caption = table.find('caption')
        if caption:
            program_name = caption.text.strip()
        else:
            program_name = "Unknown Program" # Fallback if no caption

        thead = table.find('thead')
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"] # default days
        if thead:
            header_row_days = thead.find_all('tr')
            if len(header_row_days) > 1: # check if there are at least two rows in thead
                header_row_days = header_row_days[1] # Days are in the second row of thead
                days_elements = header_row_days.find_all('th', class_='xAxis') or header_row_days.find_all('th') # handles cases where class xAxis is missing
                days = [day.text.strip() for day in days_elements] if days_elements else days # use default days if not found in the header
            elif len(header_row_days) == 1: # if only one header row, try to get days from it
                header_row_days = header_row_days[0]
                days_elements = header_row_days.find_all('th', class_='xAxis') or header_row_days.find_all('th')
                days = [day.text.strip() for day in days_elements] if days_elements else days
        else:
            print(f"Warning: <thead> tag not found in table for program: {program_name}. Using default days.")


        schedule = {}
        tbody = table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            for row in rows:
                time_header = row.find('th', class_='yAxis')
                if time_header:
                    time_slot = time_header.text.strip()
                    schedule[time_slot] = {}
                    cells = row.find_all('td')
                    day_index = 0
                    for cell in cells:
                        if day_index < len(days): # to avoid index out of range if table structure is unexpected
                            day_name = days[day_index]
                            cell_content = []
                            detailed_table = cell.find('table', class_='detailed')
                            if detailed_table:
                                detailed_rows = detailed_table.find_all('tr')
                                for detailed_row in detailed_rows:
                                    detailed_cells = detailed_row.find_all('td', class_='detailed')
                                    cell_content.extend([dc.text.strip() for dc in detailed_cells])
                                schedule[time_slot][day_name] = cell_content
                            else:
                                cell_text_content = cell.text.strip()
                                if cell_text_content:
                                    schedule[time_slot][day_name] = cell_text_content
                                else:
                                    schedule[time_slot][day_name] = "" # or None if you prefer null in JSON
                            day_index += 1

        timetable_data.append({
            "program": program_name,
            "days": days,
            "schedule": schedule
        })

    return json.dumps(timetable_data, indent=2)

if __name__ == "__main__":
    html_file = 'y3s1.html' # Replace with your html file name if different
    json_output = parse_timetable_html_to_json(html_file)
    # print(json_output)
    with open('timetable.json', 'w') as f:
        f.write(json_output)
