import csv
import ast
import jinja2
import os
import datetime


def _render_jinja_template(template_path, output_path, variables):
    path, filename = os.path.split(template_path)
    result = jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './')
    ).get_template(filename).render(variables)

    # Write to the output file
    text_file = open(output_path, "w")
    text_file.write(result)
    text_file.close()

    return True

if __name__ == "__main__":
    print("Generating configuration")

    with open('bouillonnantes_info.csv', 'rU') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|', dialect=csv.excel_tab)
        headers = reader.next()
        corrected_headers = [header.replace(" ", "_").lower() for header in headers]
        format_row_with_headers = "{%s}" % ",".join(["\"%s\": \"%%s\"" % h for h in corrected_headers])
        nodes = []
        cluster = None
        for row in reader:
            str_obj = format_row_with_headers % tuple(row)
            node_dict = ast.literal_eval(str_obj)
            node_dict["name"] = node_dict["cluster"]
            nodes += [node_dict]
            cluster = node_dict["cluster"]

        if cluster is not None:
            _render_jinja_template("templates/minimal_config.yml.jinja2",
                                   "minimal_config_bouillonnantes.yaml",
                                   {
                                       "nodes": nodes,
                                       "cluster": cluster,
                                       "now": datetime.datetime.utcnow()
                                   }
            )
        else:
            raise Exception("Could not find a cluster in the given CSV file :-(")
