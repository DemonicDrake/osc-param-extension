import csv

stored_values = [-2.1] * 256


def write_values(values):
    with open("saved_params.csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for x, value in enumerate(values):
            writer.writerow([x, value])


write_values(stored_values)