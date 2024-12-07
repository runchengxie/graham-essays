import os

# Merge all essays in the essays folder into a single md file
def merge_markdown_files(input_folder, output_file):
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for filename in sorted(os.listdir(input_folder)):
            if filename.endswith('.md'):
                filepath = os.path.join(input_folder, filename)
                with open(filepath, 'r', encoding='utf-8') as infile:
                    outfile.write(f'# {os.path.splitext(filename)[0]}\n\n')
                    outfile.write(infile.read())
                    outfile.write('\n\n')

if __name__ == '__main__':
    input_folder = './essays'  # Replace with your folder path
    output_file = 'merged_essays.md'
    merge_markdown_files(input_folder, output_file)
    print(f'Merged Markdown files into {output_file}')