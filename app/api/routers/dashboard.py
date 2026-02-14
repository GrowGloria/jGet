from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard import build_weekly_dashboard

router = APIRouter(tags=["dashboard"])

_DASHBOARD_HTML = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Dashboard</title>
    <style>
      :root {
        --bg-1: #f6f3ee;
        --bg-2: #e9edf1;
        --ink-1: #1a1a1a;
        --ink-2: #4b4b4b;
        --accent-1: #0f4c5c;
        --accent-2: #2c6e49;
        --accent-3: #c44536;
        --card: #ffffff;
        --line: #e2e6ea;
        --shadow: 0 18px 40px rgba(0, 0, 0, 0.08);
      }

      * {
        box-sizing: border-box;
      }

      body {
        margin: 0;
        font-family: "Space Grotesk", "Trebuchet MS", sans-serif;
        color: var(--ink-1);
        background: radial-gradient(1200px 800px at 15% 10%, #fcefe6 0%, transparent 60%),
          radial-gradient(1000px 700px at 85% 0%, #e6f7ff 0%, transparent 55%),
          linear-gradient(180deg, var(--bg-1) 0%, var(--bg-2) 100%);
      }

      .page {
        max-width: 1200px;
        margin: 0 auto;
        padding: 32px 20px 60px;
      }

      .hero {
        display: grid;
        gap: 16px;
        grid-template-columns: 1.2fr 0.8fr;
        align-items: center;
        margin-bottom: 28px;
      }

      .hero h1 {
        font-size: 36px;
        margin: 0;
        letter-spacing: -0.5px;
      }

      .hero p {
        margin: 8px 0 0;
        color: var(--ink-2);
        line-height: 1.5;
      }

      .chip {
        display: inline-flex;
        gap: 8px;
        align-items: center;
        padding: 8px 14px;
        border-radius: 999px;
        background: rgba(15, 76, 92, 0.08);
        color: var(--accent-1);
        font-weight: 600;
        font-size: 13px;
      }

      .grid {
        display: grid;
        gap: 16px;
      }

      .grid.cards {
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      }

      .card {
        background: var(--card);
        border-radius: 16px;
        padding: 16px;
        box-shadow: var(--shadow);
        border: 1px solid var(--line);
        animation: float-in 0.5s ease forwards;
      }

      .card h3 {
        margin: 0 0 8px;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: var(--ink-2);
      }

      .card .value {
        font-size: 26px;
        font-weight: 600;
      }

      .section {
        margin-top: 26px;
      }

      .section-title {
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        margin-bottom: 12px;
      }

      .section-title h2 {
        margin: 0;
        font-size: 20px;
      }

      .table-wrap {
        overflow-x: auto;
        border-radius: 16px;
        border: 1px solid var(--line);
        background: var(--card);
        box-shadow: var(--shadow);
      }

      table {
        width: 100%;
        border-collapse: collapse;
        min-width: 640px;
      }

      thead th {
        text-align: left;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: var(--ink-2);
        padding: 14px 16px;
        background: rgba(15, 76, 92, 0.05);
        border-bottom: 1px solid var(--line);
      }

      tbody td {
        padding: 12px 16px;
        border-bottom: 1px solid var(--line);
        font-size: 14px;
      }

      tbody tr:last-child td {
        border-bottom: none;
      }

      .pill {
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 600;
        background: rgba(44, 110, 73, 0.12);
        color: var(--accent-2);
      }

      .warning {
        color: var(--accent-3);
      }

      .muted {
        color: var(--ink-2);
      }

      .stack {
        display: grid;
        gap: 16px;
      }

      .two-col {
        display: grid;
        gap: 16px;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      }

      .form-card h3 {
        margin-bottom: 12px;
      }

      .form-grid {
        display: grid;
        gap: 12px;
      }

      .form-field {
        display: grid;
        gap: 6px;
        font-size: 13px;
        color: var(--ink-2);
      }

      .form-field input,
      .form-field textarea,
      .form-field select {
        font-family: inherit;
        font-size: 14px;
        padding: 10px 12px;
        border-radius: 10px;
        border: 1px solid var(--line);
        background: #fdfdfd;
        color: var(--ink-1);
      }

      .form-field textarea {
        resize: vertical;
        min-height: 80px;
      }

      .button {
        border: none;
        padding: 10px 16px;
        border-radius: 10px;
        background: var(--accent-1);
        color: white;
        font-weight: 600;
        cursor: pointer;
      }

      .button.secondary {
        background: var(--accent-2);
      }

      .response {
        font-family: "Courier New", monospace;
        font-size: 12px;
        white-space: pre-wrap;
        word-break: break-word;
      }

      @keyframes float-in {
        from {
          transform: translateY(8px);
          opacity: 0;
        }
        to {
          transform: translateY(0);
          opacity: 1;
        }
      }
    </style>
  </head>
  <body>
    <div class="page">
      <div class="hero">
        <div>
          <div class="chip">Weekly Dashboard</div>
          <h1>Live overview of your learning backend</h1>
          <p class="muted" id="range-text">Loading range...</p>
        </div>
        <div class="card" style="min-height: 120px;">
          <h3>Highlights</h3>
          <div class="value" id="week-highlight">--</div>
          <div class="muted" id="week-sub">---</div>
        </div>
      </div>

      <div class="section">
        <div class="section-title">
          <h2>Totals</h2>
          <span class="pill">All time</span>
        </div>
        <div class="grid cards" id="totals-grid"></div>
      </div>

      <div class="section">
        <div class="section-title">
          <h2>Weekly summary</h2>
          <span class="pill">Last 7 days</span>
        </div>
        <div class="grid cards" id="week-grid"></div>
      </div>

      <div class="section">
        <div class="section-title">
          <h2>Lesson manager</h2>
          <span class="pill">Create / Update</span>
        </div>
        <div class="two-col">
          <form class="card form-card" id="lesson-create-form">
            <h3>Create lesson</h3>
            <div class="form-grid">
              <label class="form-field">
                Group ID
                <input type="text" name="group_id" placeholder="UUID" required />
              </label>
              <label class="form-field">
                Starts at
                <input type="datetime-local" name="starts_at" required />
              </label>
              <label class="form-field">
                Ends at
                <input type="datetime-local" name="ends_at" required />
              </label>
              <label class="form-field">
                Topic
                <input type="text" name="topic" />
              </label>
              <label class="form-field">
                Plan text
                <textarea name="plan_text"></textarea>
              </label>
              <label class="form-field">
                Teacher name
                <input type="text" name="teacher_name" />
              </label>
              <label class="form-field">
                Cabinet text
                <input type="text" name="cabinet_text" />
              </label>
              <label class="form-field">
                Status
                <select name="status">
                  <option value="scheduled" selected>scheduled</option>
                  <option value="cancelled">cancelled</option>
                  <option value="completed">completed</option>
                </select>
              </label>
              <button class="button" type="submit">Create lesson</button>
            </div>
          </form>

          <form class="card form-card" id="lesson-update-form">
            <h3>Update lesson</h3>
            <div class="form-grid">
              <label class="form-field">
                Lesson ID
                <input type="text" name="lesson_id" placeholder="UUID" required />
              </label>
              <label class="form-field">
                Group ID (optional)
                <input type="text" name="group_id" placeholder="UUID" />
              </label>
              <label class="form-field">
                Starts at (optional)
                <input type="datetime-local" name="starts_at" />
              </label>
              <label class="form-field">
                Ends at (optional)
                <input type="datetime-local" name="ends_at" />
              </label>
              <label class="form-field">
                Topic (optional)
                <input type="text" name="topic" />
              </label>
              <label class="form-field">
                Plan text (optional)
                <textarea name="plan_text"></textarea>
              </label>
              <label class="form-field">
                Teacher name (optional)
                <input type="text" name="teacher_name" />
              </label>
              <label class="form-field">
                Cabinet text (optional)
                <input type="text" name="cabinet_text" />
              </label>
              <label class="form-field">
                Status (optional)
                <select name="status">
                  <option value="">--</option>
                  <option value="scheduled">scheduled</option>
                  <option value="cancelled">cancelled</option>
                  <option value="completed">completed</option>
                </select>
              </label>
              <button class="button secondary" type="submit">Update lesson</button>
            </div>
          </form>
        </div>
        <div class="card" id="lesson-response">
          <h3>Response</h3>
          <div class="response" id="lesson-response-text">No actions yet.</div>
        </div>
      </div>

      <div class="section">
        <div class="section-title">
          <h2>Daily tables</h2>
          <span class="pill">Per day</span>
        </div>
        <div class="stack" id="tables"></div>
      </div>
    </div>

    <script>
      const basePath = window.location.pathname.replace(/\/dashboard\/?$/, "");
      const fmtNumber = (value) =>
        new Intl.NumberFormat("en-US").format(value ?? 0);

      const fmtDate = (value) => {
        if (!value) return "-";
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return value;
        return date.toISOString().slice(0, 10);
      };

      const tableConfig = {
        users_by_day: { title: "Users created", columns: ["date", "count"] },
        groups_by_day: { title: "Groups created", columns: ["date", "count"] },
        students_by_day: { title: "Students created", columns: ["date", "count"] },
        lessons_by_day: { title: "Lessons created / starting", columns: ["date", "created", "starting"] },
        lesson_participations_by_day: { title: "Lesson participation updates", columns: ["date", "count"] },
        materials_by_day: { title: "Materials created", columns: ["date", "count"] },
        notifications_by_day: { title: "Notifications created", columns: ["date", "count"] },
        payments_by_day: { title: "Payments activity", columns: ["date", "count", "amount_cents", "paid_count", "paid_amount_cents"] },
        device_tokens_by_day: { title: "Device tokens created", columns: ["date", "count"] },
        managers_by_day: { title: "Managers created", columns: ["date", "count"] },
      };

      const columnsLabel = {
        date: "Date",
        count: "Count",
        created: "Created",
        starting: "Starting",
        amount_cents: "Amount (cents)",
        paid_count: "Paid",
        paid_amount_cents: "Paid amount (cents)",
      };

      const totalsOrder = [
        ["users", "Users"],
        ["users_admin", "Admins"],
        ["users_parent", "Parents"],
        ["groups", "Groups"],
        ["students", "Students"],
        ["lessons", "Lessons"],
        ["lesson_participations", "Lesson participations"],
        ["materials", "Materials"],
        ["notifications", "Notifications"],
        ["payments", "Payments"],
        ["device_tokens", "Device tokens"],
        ["managers", "Managers"],
      ];

      const weekOrder = [
        ["users_created", "Users created"],
        ["groups_created", "Groups created"],
        ["students_created", "Students created"],
        ["lessons_created", "Lessons created"],
        ["lessons_starting", "Lessons starting"],
        ["lesson_participations_updated", "Participation updates"],
        ["materials_created", "Materials created"],
        ["notifications_created", "Notifications created"],
        ["payments_created", "Payments created"],
        ["payments_amount_cents", "Payments amount"],
        ["payments_paid", "Paid payments"],
        ["payments_paid_amount_cents", "Paid amount"],
        ["device_tokens_created", "Device tokens created"],
        ["managers_created", "Managers created"],
      ];

      const buildCard = (label, value) => {
        const card = document.createElement("div");
        card.className = "card";
        card.innerHTML = `<h3>${label}</h3><div class="value">${fmtNumber(value)}</div>`;
        return card;
      };

      const buildTable = (table) => {
        const config = tableConfig[table.name] || { title: table.name, columns: ["date", "count"] };
        const wrapper = document.createElement("div");
        wrapper.className = "table-wrap";

        const tableEl = document.createElement("table");
        const thead = document.createElement("thead");
        const headerRow = document.createElement("tr");
        config.columns.forEach((col) => {
          const th = document.createElement("th");
          th.textContent = columnsLabel[col] || col;
          headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        tableEl.appendChild(thead);

        const tbody = document.createElement("tbody");
        table.rows.forEach((row) => {
          const tr = document.createElement("tr");
          config.columns.forEach((col) => {
            const td = document.createElement("td");
            const raw = row[col];
            if (col === "date") {
              td.textContent = fmtDate(raw);
            } else {
              td.textContent = fmtNumber(raw ?? 0);
            }
            tr.appendChild(td);
          });
          tbody.appendChild(tr);
        });
        tableEl.appendChild(tbody);
        wrapper.appendChild(tableEl);

        const container = document.createElement("div");
        container.className = "stack";
        const title = document.createElement("div");
        title.className = "section-title";
        title.innerHTML = `<h2>${config.title}</h2>`;
        container.appendChild(title);
        container.appendChild(wrapper);
        return container;
      };

      const render = (data) => {
        const rangeText = document.getElementById("range-text");
        rangeText.textContent = `${data.range.from_date} -> ${data.range.to_date} (${data.range.days} days, ${data.range.timezone})`;

        const totalsGrid = document.getElementById("totals-grid");
        totalsGrid.innerHTML = "";
        totalsOrder.forEach(([key, label]) => {
          totalsGrid.appendChild(buildCard(label, data.totals[key]));
        });

        const weekGrid = document.getElementById("week-grid");
        weekGrid.innerHTML = "";
        weekOrder.forEach(([key, label]) => {
          weekGrid.appendChild(buildCard(label, data.week[key]));
        });

        const highlight = document.getElementById("week-highlight");
        const weekSub = document.getElementById("week-sub");
        highlight.textContent = fmtNumber(data.week.lessons_starting);
        weekSub.textContent = "Lessons starting this week";

        const tables = document.getElementById("tables");
        tables.innerHTML = "";
        data.tables.forEach((table) => {
          tables.appendChild(buildTable(table));
        });
      };

      const load = async () => {
        const res = await fetch(`${basePath}/dashboard/weekly`);
        if (!res.ok) {
          throw new Error("Failed to load dashboard data");
        }
        const data = await res.json();
        render(data);
      };

      const responseBox = document.getElementById("lesson-response-text");

      const setResponse = (title, payload, isError = false) => {
        const header = isError ? "ERROR" : "OK";
        responseBox.textContent = `${header}: ${title}\n${JSON.stringify(payload, null, 2)}`;
        responseBox.classList.toggle("warning", isError);
      };

      const toIso = (value) => {
        if (!value) return null;
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return null;
        return date.toISOString();
      };

      const pickValue = (form, name) => {
        const input = form.querySelector(`[name="${name}"]`);
        if (!input) return "";
        return (input.value || "").trim();
      };

      const createForm = document.getElementById("lesson-create-form");
      const updateForm = document.getElementById("lesson-update-form");

      createForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const payload = {
          group_id: pickValue(createForm, "group_id"),
          starts_at: toIso(pickValue(createForm, "starts_at")),
          ends_at: toIso(pickValue(createForm, "ends_at")),
          topic: pickValue(createForm, "topic") || null,
          plan_text: pickValue(createForm, "plan_text") || null,
          teacher_name: pickValue(createForm, "teacher_name") || null,
          cabinet_text: pickValue(createForm, "cabinet_text") || null,
          status: pickValue(createForm, "status") || "scheduled",
        };

        if (!payload.group_id || !payload.starts_at || !payload.ends_at) {
          setResponse("Missing required fields", payload, true);
          return;
        }

        try {
          const res = await fetch(`${basePath}/lessons`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          });
          const data = await res.json();
          if (!res.ok) {
            setResponse("Create failed", data, true);
            return;
          }
          setResponse("Lesson created", data, false);
          load();
        } catch (err) {
          setResponse("Create failed", { message: err.message }, true);
        }
      });

      updateForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const lessonId = pickValue(updateForm, "lesson_id");
        if (!lessonId) {
          setResponse("Lesson ID required", {}, true);
          return;
        }

        const data = {};
        const groupId = pickValue(updateForm, "group_id");
        if (groupId) data.group_id = groupId;
        const startsAt = toIso(pickValue(updateForm, "starts_at"));
        if (startsAt) data.starts_at = startsAt;
        const endsAt = toIso(pickValue(updateForm, "ends_at"));
        if (endsAt) data.ends_at = endsAt;
        const topic = pickValue(updateForm, "topic");
        if (topic) data.topic = topic;
        const planText = pickValue(updateForm, "plan_text");
        if (planText) data.plan_text = planText;
        const teacherName = pickValue(updateForm, "teacher_name");
        if (teacherName) data.teacher_name = teacherName;
        const cabinetText = pickValue(updateForm, "cabinet_text");
        if (cabinetText) data.cabinet_text = cabinetText;
        const status = pickValue(updateForm, "status");
        if (status) data.status = status;

        try {
          const res = await fetch(`${basePath}/lessons/${lessonId}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
          });
          const payload = await res.json();
          if (!res.ok) {
            setResponse("Update failed", payload, true);
            return;
          }
          setResponse("Lesson updated", payload, false);
          load();
        } catch (err) {
          setResponse("Update failed", { message: err.message }, true);
        }
      });

      load().catch((err) => {
        document.getElementById("range-text").textContent = "Failed to load dashboard.";
        document.getElementById("week-highlight").textContent = "Error";
        document.getElementById("week-sub").textContent = err.message;
      });
    </script>
  </body>
</html>
"""


@router.get("/dashboard/weekly", response_model=DashboardResponse)
async def weekly_dashboard(session: AsyncSession = Depends(get_session)):
    return await build_weekly_dashboard(session)


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page():
    return HTMLResponse(_DASHBOARD_HTML)
