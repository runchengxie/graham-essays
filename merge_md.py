import os

def merge_files(input_folder, output_md, output_txt):
    # Merge to markdown
    with open(output_md, 'w', encoding='utf-8') as md_file, \
         open(output_txt, 'w', encoding='utf-8') as txt_file:
        
        for filename in sorted(os.listdir(input_folder)):
            if filename.endswith('.md'):
                filepath = os.path.join(input_folder, filename)
                with open(filepath, 'r', encoding='utf-8') as infile:
                    content = infile.read()
                    
                    # Write to markdown file
                    md_file.write(f'# {os.path.splitext(filename)[0]}\n\n')
                    md_file.write(content)
                    md_file.write('\n\n')
                    
                    # Write to text file (without markdown formatting)
                    txt_file.write(f'{os.path.splitext(filename)[0]}\n\n')
                    txt_file.write(content.replace('#', '').replace('*', ''))
                    txt_file.write('\n\n')

if __name__ == '__main__':
    input_folder = './essays'
    output_md = 'merged_essays.md'
    output_txt = 'merged_essays.txt'
    
    merge_files(input_folder, output_md, output_txt)
    print(f'Merged files created: {output_md} and {output_txt}')