const cheerio = require("cheerio");
const fs = require("fs");

function extractTimetableData(htmlFilePath, outputJsonPath) {
  const htmlContent = fs.readFileSync(htmlFilePath, "utf-8");
  const $ = cheerio.load(htmlContent);

  const timetableData = [];

  $('table[id^="table_"]').each((index, tableElement) => {
    // Select tables with IDs starting with "table_"
    const table = $(tableElement);
    const groupName = table.find("caption").text().trim() || "Unknown Group";
    const tableId = table.attr("id");
    const groupTimetable = {
      group: groupName,
      table_id: tableId,
      schedule: {},
    };

    const daysHeaderRow = table.find("thead tr:nth-child(2)"); // Get the second row in thead for days
    const days = [];
    daysHeaderRow.find("th.xAxis").each((i, th) => {
      days.push($(th).text().trim());
    });

    table.find("tbody tr").each((rowIndex, rowElement) => {
      const row = $(rowElement);
      const timeSlotCell = row.find("th.yAxis");
      if (timeSlotCell.length === 0) {
        // Skip header rows within tbody if any
        return;
      }
      const timeSlot = timeSlotCell.text().trim();
      groupTimetable.schedule[timeSlot] = {};

      row.find("td").each((dayIndex, dayCellElement) => {
        const dayCell = $(dayCellElement);
        const dayName = days[dayIndex];
        groupTimetable.schedule[timeSlot][dayName] = [];

        const detailedTable = dayCell.find("table.detailed");
        if (detailedTable.length > 0) {
          const classInfo = [];
          detailedTable
            .find("tr")
            .each((detailedRowIndex, detailedRowElement) => {
              $(detailedRowElement)
                .find("td.detailed")
                .each((detailedDataIndex, detailedDataElement) => {
                  classInfo.push($(detailedDataElement).text().trim());
                });
            });
          groupTimetable.schedule[timeSlot][dayName].push(classInfo);
        } else if (
          dayCell.text().trim() &&
          dayCell.text().trim() !== "---" &&
          dayCell.text().trim() !== "-x-"
        ) {
          groupTimetable.schedule[timeSlot][dayName].push([
            dayCell.text().trim(),
          ]);
        } else {
          groupTimetable.schedule[timeSlot][dayName].push([]); // Empty slot
        }
      });
    });
    timetableData.push(groupTimetable);
  });

  fs.writeFileSync(
    outputJsonPath,
    JSON.stringify(timetableData, null, 4),
    "utf-8"
  );
  console.log(`Timetable data extracted and saved to ${outputJsonPath}`);
}

const htmlFile = "y3s1.html";
const jsonFile = "timetable_data.json";
extractTimetableData(htmlFile, jsonFile);
