const fs = require("fs");
const cheerio = require("cheerio");

const htmlFilePath = "/workspaces/timetable-py/y3s1.html";
const outputFilePath = "/workspaces/timetable-py/timetable.json";

fs.readFile(htmlFilePath, "utf8", (err, data) => {
  if (err) {
    console.error("Error reading HTML file:", err);
    return;
  }

  const $ = cheerio.load(data);
  const tables = $("table");
  const timetable = [];

  tables.each((index, table) => {
    const group = $(table).find('th[colspan="5"]').text().trim();
    const rows = $(table).find("tbody tr");

    rows.each((rowIndex, row) => {
      const time = $(row).find("th.yAxis").text().trim();
      const cells = $(row).find("td");

      cells.each((cellIndex, cell) => {
        const cellContent = $(cell).html();
        if (cellContent && cellContent.includes("<br />")) {
          const details = cellContent
            .split("<br />")
            .map((item) => $(item).text().trim());
          const [module, lectureType, lecturers, location] = details;

          timetable.push({
            group,
            time,
            day: $(table)
              .find(`th.xAxis:nth-child(${cellIndex + 2})`)
              .text()
              .trim(),
            module,
            lectureType,
            lecturers: lecturers.split(", "),
            location,
          });
        }
      });
    });
  });

  fs.writeFile(outputFilePath, JSON.stringify(timetable, null, 2), (err) => {
    if (err) {
      console.error("Error writing JSON file:", err);
      return;
    }
    console.log("Timetable data extracted to JSON file successfully.");
  });
});
