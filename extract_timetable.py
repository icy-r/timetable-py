from bs4 import BeautifulSoup
import json

def parse_timetable(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    all_tables = soup.find_all('table', id=lambda x: x and x.startswith('table_'))
    timetables = []
    
    for table in all_tables:
        group_th = table.find('th', colspan='5')
        if not group_th:
            continue
            
        group_name = group_th.text.strip()
        days = [th.text.strip() for th in table.find_all('th', class_='xAxis')]
        schedule = parse_schedule(table, days)
        timetables.append({'group': group_name, 'schedule': schedule})
    
    return timetables

def parse_schedule(table, days):
    schedule = {}
    tbody = table.find('tbody')
    if not tbody:
        return schedule
        
    rows = tbody.find_all('tr')
    pending = {day: None for day in days}
    
    for row in rows:
        time_slot = row.find('th', class_='yAxis')
        if not time_slot:
            continue
            
        time = time_slot.text.strip()
        schedule[time] = {}
        cells = row.find_all('td', recursive=False)
        cell_index = 0

        for day in days:
            if pending[day]:
                # Handle pending rowspan cell
                cell_data = extract_cell_data(pending[day]['cell'])
                pending[day]['rows_left'] -= 1
                if pending[day]['rows_left'] == 0:
                    pending[day] = None
                schedule[time][day] = cell_data
            else:
                # Handle new cell
                if cell_index < len(cells):
                    cell = cells[cell_index]
                    cell_index += 1
                    cell_data = extract_cell_data(cell)
                    schedule[time][day] = cell_data
                    
                    # Check for rowspan
                    if cell.has_attr('rowspan'):
                        try:
                            span = int(cell['rowspan'])
                            if span > 1:
                                pending[day] = {'cell': cell, 'rows_left': span - 1}
                        except ValueError:
                            pass
                else:
                    schedule[time][day] = None

    return schedule

def extract_cell_data(cell):
    # Handle empty or special cells
    text = cell.get_text("\n", strip=True)
    if text in ['---', '-x-']:
        return None
        
    # Handle detailed table cells
    detailed = cell.find('table', class_='detailed')
    if detailed:
        rows = detailed.find_all('tr')
        if len(rows) >= 4:
            return {
                "groups": [g.strip() for g in rows[0].get_text(strip=True).split(",")],
                "lecture": rows[1].get_text(strip=True),
                "lecturers": [l.strip() for l in rows[2].get_text(strip=True).split(",")],
                "hall": rows[3].get_text(strip=True)
            }
            
    # Handle regular cells
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if not lines:
        return None
        
    # Handle group-based format
    if lines and "," in lines[0] and any(x in lines[0] for x in ["Y3", "Y2", "Y1"]):
        return {
            "groups": [g.strip() for g in lines[0].split(",")],
            "lecture": lines[1] if len(lines) > 1 else "",
            "lecturers": [lines[2]] if len(lines) > 2 else [],
            "hall": lines[3] if len(lines) > 3 else ""
        }
    
    # Return simple format
    return lines if lines else None

def save_to_json(timetables, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(timetables, f, indent=2, ensure_ascii=False)

def main():
    with open('y3s1.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    timetables = parse_timetable(html_content)
    save_to_json(timetables, 'timetable.json')

if __name__ == "__main__":
    main()