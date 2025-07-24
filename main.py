import os
import sqlite3
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Employee API")

def get_db_connection():
    conn = sqlite3.connect("employees.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Employees (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Department TEXT NOT NULL,
            Email TEXT NOT NULL UNIQUE
        )
    ''')
    sample_employees = [
        ('Tharun Iyer', 'Finance', 'tharun.iyer@example.com'),
        ('Deepa Rao', 'IT', 'deepa.rao@example.com'),
        ('Ramya Subramanian', 'IT', 'ramya.subramanian@example.com'),
        ('Lavanya Shetty', 'IT', 'lavanya.shetty@example.com'),
        ('Ishaan Subramanian', 'HR', 'ishaan.subramanian@example.com'),
        ('Sathish Rao', 'HR', 'sathish.rao@example.com'),
        ('Charan Reddy', 'IT', 'charan.reddy@example.com'),
        ('Harini Subramanian', 'IT', 'harini.subramanian@example.com'),
        ('Bhavana Srinivasan', 'IT', 'bhavana.srinivasan@example.com'),
        ('Deepa Iyer', 'HR', 'deepa.iyer@example.com'),
        ('Vignesh Reddy', 'IT', 'vignesh.reddy@example.com'),
        ('Yamini Krishnan', 'Finance', 'yamini.krishnan@example.com'),
        ('Manoj Pillai', 'IT', 'manoj.pillai@example.com'),
        ('Bhavana Rao', 'HR', 'bhavana.rao@example.com'),
        ('Tharun Naidu', 'Finance', 'tharun.naidu@example.com'),
        ('Sathish Krishnan', 'Finance', 'sathish.krishnan@example.com'),
        ('Vignesh Gopal', 'HR', 'vignesh.gopal@example.com'),
        ('Yamini Das', 'IT', 'yamini.das@example.com'),
        ('Usha Menon', 'HR', 'usha.menon@example.com'),
        ('Pranav Reddy', 'HR', 'pranav.reddy@example.com'),
        ('Oviya Ilango', 'HR', 'oviya.ilango@example.com'),
        ('Bhargavi Natarajan', 'IT', 'bhargavi.natarajan@example.com'),
        ('Ulaganathan Eashwaran', 'HR', 'ulaganathan.eashwaran@example.com'),
        ('Nandhini Loganathan', 'Finance', 'nandhini.loganathan@example.com'),
        ('Yugendran Ilango', 'HR', 'yugendran.ilango@example.com'),
        ('Dinesh Jagadeesh', 'Finance', 'dinesh.jagadeesh@example.com'),
        ('Sharanya Natarajan', 'HR', 'sharanya.natarajan@example.com'),
        ('Sharanya Zachariah', 'HR', 'sharanya.zachariah@example.com'),
        ('Lakshmi Ranganathan', 'HR', 'lakshmi.ranganathan@example.com'),
        ('Ulaganathan Jagadeesh', 'IT', 'ulaganathan.jagadeesh@example.com'),
        ('Lakshmi Thangaraj', 'Finance', 'lakshmi.thangaraj@example.com'),
        ('Revansh Hariharan', 'HR', 'revansh.hariharan@example.com'),
        ('Ajay Zachariah', 'Finance', 'ajay.zachariah@example.com'),
        ('Ulaganathan Balaji', 'Finance', 'ulaganathan.balaji@example.com'),
        ('Ulaganathan Loganathan', 'IT', 'ulaganathan.loganathan@example.com'),
        ('Thamizh Ranganathan', 'Finance', 'thamizh.ranganathan@example.com'),
        ('Mahesh Natarajan', 'HR', 'mahesh.natarajan@example.com'),
        ('Bhargavi Darshan', 'Finance', 'bhargavi.darshan@example.com'),
        ('Oviya Sekhar', 'IT', 'oviya.sekhar@example.com'),
        ('Varun Yegneswaran', 'Finance', 'varun.yegneswaran@example.com'),
        ('Oviya Udhayakumar', 'IT', 'oviya.udhayakumar@example.com'),
        ('Keerthi Muthuraj', 'IT', 'keerthi.muthuraj@example.com'),
        ('Jayanth Natarajan', 'HR', 'jayanth.natarajan@example.com')
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO Employees (Name, Department, Email) VALUES (?, ?, ?)",
        sample_employees
    )
    conn.commit()
    conn.close()

init_db()

class Employee(BaseModel):
    Id: int
    Name: str
    Department: str
    Email: str

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Employee API"}

@app.get("/employees", response_model=List[Employee])
def get_employees():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Id, Name, Department, Email FROM Employees")
    rows = cursor.fetchall()
    employees = [Employee(Id=row[0], Name=row[1], Department=row[2], Email=row[3]) for row in rows]
    conn.close()
    return employees

@app.post("/run_query")
async def run_query(request: Request):
    data = await request.json()
    sql_query = data.get("query")
    if not sql_query:
        raise HTTPException(status_code=400, detail="No query provided")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        try:
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
        except:
            results = {"message": "Query executed (no results to fetch)"}
        conn.commit()
        conn.close()
        return JSONResponse(content={"results": results})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

@app.get("/ui", response_class=HTMLResponse)
def serve_ui():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
      <title>SQL Query Runner</title>
      <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7fa; color: #333; padding: 40px; display: flex; flex-direction: column; align-items: center; min-height: 100vh; margin: 0; }
        h2 { margin-bottom: 20px; color: #2c3e50; font-weight: 600; }
        textarea { width: 600px; max-width: 90vw; height: 140px; font-family: Consolas, monospace; font-size: 16px; padding: 15px; border: 2px solid #2980b9; border-radius: 6px; resize: vertical; box-sizing: border-box; transition: border-color 0.3s ease; }
        textarea:focus { outline: none; border-color: #1abc9c; box-shadow: 0 0 8px rgba(26, 188, 156, 0.5); }
        button { margin-top: 15px; background-color: #2980b9; color: white; border: none; padding: 12px 30px; font-size: 16px; cursor: pointer; border-radius: 6px; transition: background-color 0.3s ease; user-select: none; }
        button:hover { background-color: #1abc9c; }
        pre { margin-top: 30px; width: 600px; max-width: 90vw; background-color: #272822; color: #f8f8f2; font-family: Consolas, monospace; padding: 20px; border-radius: 6px; overflow-x: auto; box-sizing: border-box; white-space: pre-wrap; word-wrap: break-word; min-height: 150px; }
        @media (max-width: 650px) { textarea, pre { width: 100%; } }
      </style>
    </head>
    <body>
      <h2>Run SQL Query</h2>
      <textarea id="query" rows="5" cols="60">SELECT * FROM Employees</textarea><br>
      <button onclick="runQuery()">Run</button><br><br>
      <div id="result"></div>
      <script>
        async function runQuery() {
          const query = document.getElementById('query').value;
          const res = await fetch('/run_query', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query})
          });
          const data = await res.json();
          if (data.error) {
            document.getElementById('result').innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
            return;
          }
          if (Array.isArray(data.results)) {
            const rows = data.results;
            if (rows.length === 0) {
              document.getElementById('result').innerHTML = "<p>No results.</p>";
              return;
            }
            const headers = Object.keys(rows[0]);
            let html = "<table border='1' cellpadding='6' style='border-collapse:collapse;'><thead><tr>";
            for (const header of headers) { html += `<th>${header}</th>`; }
            html += "</tr></thead><tbody>";
            for (const row of rows) {
              html += "<tr>";
              for (const header of headers) { html += `<td>${row[header]}</td>`; }
              html += "</tr>";
            }
            html += "</tbody></table>";
            document.getElementById('result').innerHTML = html;
          } else {
            document.getElementById('result').innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
          }
        }
      </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)