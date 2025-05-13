import os
from nbconvert.preprocessors import ExecutePreprocessor


def main():
    # render quarto book
    text = "conda activate safety_data_env && quarto render " + os.path.join(r"demo") + " --execute"
    os.system(text)
    print("notebook created")

if __name__ == "__main__":
    main()
