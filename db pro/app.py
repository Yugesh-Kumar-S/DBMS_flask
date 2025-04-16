from flask import Flask, request, jsonify, render_template
import cx_Oracle

app = Flask(__name__)

dsn_tns = cx_Oracle.makedsn("localhost", 1521, service_name="XE")
conn = cx_Oracle.connect(user="yugi", password="yugi", dsn=dsn_tns)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/students', methods=['GET'])
def get_students():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student")
    students = [
        {"reg_no": row[0], "name": row[1], "category": row[2], "verification": row[3] if row[3] else "No"}
        for row in cursor.fetchall()
    ]
    cursor.close()
    return jsonify(students)

@app.route('/lateral_students', methods=['GET'])
def get_lateral_students():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lateral_student")
    lateral_students = [
        {"reg_no": row[0], "name": row[1], "category": row[2], "verification": row[3] if row[3] else "No"}
        for row in cursor.fetchall()
    ]
    cursor.close()
    return jsonify(lateral_students)

@app.route('/students', methods=['POST'])
def add_student():
    data = request.json
    reg_no = data.get("reg_no")
    name = data.get("name")

    if not reg_no or not name:
        return jsonify({"error": "Missing data"}), 400

    cursor = conn.cursor()

    if reg_no.startswith("2024"):
        category, verify = "lateral", "Yes"
        cursor.execute("INSERT INTO student (reg_no, name, category, verification) VALUES (:1, :2, :3, :4)",
                       (reg_no, name, category, verify))
        cursor.execute("INSERT INTO lateral_student (reg_no, name, category, verification) VALUES (:1, :2, :3, :4)",
                       (reg_no, name, category, verify))
    elif reg_no.startswith("20235030"):
        category, verify = "r", "No"
        cursor.execute("INSERT INTO student (reg_no, name, category, verification) VALUES (:1, :2, :3, :4)",
                       (reg_no, name, category, verify))
    else:
        category, verify = "ss", "No"
        cursor.execute("INSERT INTO student (reg_no, name, category, verification) VALUES (:1, :2, :3, :4)",
                       (reg_no, name, category, verify))

    cursor.close()
    return jsonify({"message": "Student inserted successfully!"})

@app.route('/students/<reg_no>', methods=['DELETE'])
def delete_student(reg_no):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM student WHERE reg_no = :1", (reg_no,))
    conn.commit()
    cursor.close()
    return jsonify({"message": "Student deleted successfully!"})

@app.route('/lateral_students/<reg_no>', methods=['DELETE'])
def delete_lateral_student(reg_no):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM lateral_student WHERE reg_no = :1", (reg_no,))
    conn.commit()
    cursor.close()
    return jsonify({"message": "Lateral student deleted successfully!"})

@app.route('/commit', methods=['POST'])
def commit_changes():
    try:
        conn.commit()
        return jsonify({"message": "Changes committed successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/rollback', methods=['POST'])
def rollback_changes():
    try:
        conn.rollback()
        return jsonify({"message": "Changes rolled back successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
