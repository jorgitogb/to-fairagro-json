import argparse
from pathlib import Path
from to_dataverse_json import DataverseConverter

def main():
    parser = argparse.ArgumentParser(description='RO-Crate/Schema.org to Dataverse JSON Converter')
    parser.add_argument('input', help='Input path (file or directory)')
    parser.add_argument('--type', choices=['rocrate', 'schemaorg'], required=True, help='Input type')
    parser.add_argument('--output', help='Output JSON path (defaults to output/<input_filename>.json)')

    args = parser.parse_args()
    
    output_path = args.output
    if not output_path:
        input_name = Path(args.input).stem
        output_path = f"output/{input_name}.dataverse.json"

    converter = DataverseConverter()

    converter.load(args.input)
    converter.convert(output_path)
    print(f"Successfully converted {args.input} to {output_path}")

if __name__ == "__main__":
    main()
