import os
import re
import subprocess
import time

def save_results(job_title, job_company, resume, user_assessment):
    directory_name = (job_title + job_company).lower()
    directory_name = directory_name.replace(" ", "_")
    directory_name = re.sub(r'[^a-z0-9_\-]', '', directory_name)

    os.makedirs("../../output/" + directory_name, exist_ok=False)

    with open("../../output/" + directory_name + '/main.tex', "w", encoding='utf-8') as file:
        file.write(resume)

    print(f"File created at ../../output/" + directory_name + '/main.tex')
    time.sleep(10)
    print(f"Compiling latex...")
    file = compile_latex_system('main.tex', "../../output/" + directory_name)
    cleanup_latex_files("../../output/" + directory_name)

    output_user_assessment(user_assessment, "../../output/" + directory_name)


    return


def compile_latex(latex_file, latex_directory):
    # start_time = time.time()
    # while not os.path.exists(latex_directory):
    #     elapsed_time = time.time() - start_time
    #     if elapsed_time > 60:
    #         print(f"Error: LaTeX directory '{latex_directory}' did not exist after 1 minute.")
    #         return None
    #     print(f"Waiting for directory to appear in OS.")
    #     time.sleep(5)  # Check every 5 seconds
    # print(f"Directory apparead in OS")

    try:
        command = ['pdflatex', latex_file]
        process = subprocess.Popen(command, cwd=latex_directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        while True:
            output = process.stdout.readline()
            # if output:
            #     print(output.decode().strip())
            error = process.stderr.readline()
            if error:
                print(f"Error: {error.decode().strip()}")

            return_code = process.poll()
            if return_code is not None:
                if return_code == 0:
                    print(f"\nSuccessfully finished compiling '{latex_file}' into PDF.")
                    pdf_file = latex_file.replace('.tex', '.pdf')
                    return pdf_file
                else:
                    print(f"\nCompilation of '{latex_file}' failed with return code: {return_code}")
                    return None
                break
            time.sleep(0.1)  # Small delay to avoid busy-waiting

    except FileNotFoundError:
        print("Error: 'pdflatex' command not found. Make sure LaTeX is installed and in your system's PATH.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def compile_latex_system(latex_file, latex_directory):
    if os.path.exists(os.path.join(latex_directory, latex_file)):
        if os.name == 'nt':  # Windows
            null_device = 'NUL'
        else:  # Unix-like
            null_device = '/dev/null'

        command = f"cd \"{latex_directory}\" && pdflatex -interaction=nonstopmode \"{latex_file}\" > {null_device} 2>&1"
        return_code = os.system(command)

        if return_code == 0:
            print(f"Successfully compiled '{latex_file}' in '{latex_directory}'")
        else:
            print(f"Error compiling '{latex_file}' in '{latex_directory}' (return code: {return_code})")
    else:
        print(f"Error: LaTeX file '{latex_file}' not found in '{latex_directory}'.")

def cleanup_latex_files(directory):
    """
    Deletes main.aux and main.log files in the specified directory.
    """
    aux_file = os.path.join(directory, 'main.aux')
    log_file = os.path.join(directory, 'main.log')

    deleted_count = 0

    for f in [aux_file, log_file]:
        if os.path.exists(f):
            try:
                os.remove(f)
                # print(f"Deleted: {f}")
                deleted_count += 1
            except OSError as e:
                print(f"Error deleting {f}: {e}")

    if deleted_count > 0:
        print(f"Successfully deleted {deleted_count} auxiliary files in '{directory}'.")
    else:
        print(f"No main.aux or main.log found in '{directory}'.")

def output_user_assessment(data_dict, filepath):
    try:
        with open(filepath + '/comments.txt', 'w', encoding='utf-8') as f:
            for key, value in data_dict.items():
                f.write(f"{key}: {value}\n")
        print(f"Dictionary data successfully written to '{filepath}'.")
    except Exception as e:
        print(f"An error occurred while writing to '{filepath}': {e}")


if __name__ == "__main__":
    resume = r"""
    \documentclass{article}
    \begin{document}
    Hello, MiKTeX!
    \end{document}
    """
    comments = {'profile_fit': 'strong',
                'education_requirements_met': 'strong',
                'knowledge_requirements_met': 'strong',
                'years_of_experience_met': 'strong',
                'summary': 'good good very good job indeed you will get a job strong ant'}


    save_results("job_posting", "ashitionyx", resume, user_assessment=comments)