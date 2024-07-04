import subprocess

# 运行 generate_mapping.py
print("Running generate_mapping.py...")
subprocess.run(["python", "generate_mapping.py"])

# 运行 visual_chart.py
print("Running visual_chart.py...")
subprocess.run(["python", "visual_chart.py"])

print("Both scripts have been executed.")
