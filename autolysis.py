import os
import glob
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import chardet

def find_csv_files():
    """
    Find all CSV files in the current directory
    """
    return glob.glob('*.csv')

def safe_read_csv(file_path):
    """
    Safely read CSV file with encoding detection
    """
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding'] or 'utf-8'

    encodings_to_try = [
        encoding, 
        'utf-8', 
        'latin-1', 
        'iso-8859-1', 
        'cp1252'
    ]

    for enc in encodings_to_try:
        try:
            return pd.read_csv(file_path, encoding=enc)
        except Exception:
            continue

    raise ValueError(f"Unable to read file {file_path} with any standard encoding")

def analyze_data(df):
    """
    Perform basic data analysis
    """
    description = df.describe().to_dict()
    missing_values = df.isnull().sum().to_dict()

    numeric_df = df.select_dtypes(include=['number'])
    correlation = numeric_df.corr().to_dict() if not numeric_df.empty else {}

    return {
        'description': description,
        'missing_values': missing_values,
        'correlation': correlation
    }

def generate_narrative(df, analysis):
    """
    Generate a narrative summary of the dataset
    """
    narrative = []

    # Missing values analysis
    missing_count = sum(analysis['missing_values'].values())
    if missing_count > 0:
        narrative.append(f"There are {missing_count} missing values across the dataset.")
    else:
        narrative.append("There are no missing values in the dataset.")

    # Data distribution
    narrative.append("\n### Data Distribution Insights")
    for column, stats in analysis['description'].items():
        mean = stats.get('mean', 'N/A')
        std = stats.get('std', 'N/A')
        narrative.append(f"- Column '{column}' has a mean of {mean} and a standard deviation of {std}.")

    # Correlation insights
    if analysis['correlation']:
        narrative.append("\n### Correlation Insights")
        for column, correlations in analysis['correlation'].items():
            for correlated_column, corr_value in correlations.items():
                if abs(corr_value) > 0.5:  # Highlight significant correlations
                    narrative.append(f"- Strong correlation between '{column}' and '{correlated_column}': {corr_value:.2f}")

    return "\n".join(narrative)

def create_visualizations(df, output_dir, file_name):
    """
    Generate and save visualizations
    """
    os.makedirs(output_dir, exist_ok=True)

    # Check if seaborn style is available
    if 'seaborn' in plt.style.available:
        plt.style.use('seaborn')
    else:
        plt.style.use('ggplot')  # Fallback to 'ggplot' if seaborn is not available

    numeric_columns = df.select_dtypes(include=['number']).columns.tolist()

    for column in numeric_columns[:3]:
        plt.figure(figsize=(10, 6))
        sns.histplot(df[column], kde=True)
        plt.title(f'Distribution of {column} in {file_name}')
        plt.xlabel(column)
        plt.ylabel('Frequency')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'{column}_distribution.png'))
        plt.close()

    if len(numeric_columns) > 1:
        plt.figure(figsize=(12, 10))
        correlation_matrix = df[numeric_columns].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
        plt.title(f'Correlation Heatmap for {file_name}')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'correlation_heatmap.png'))
        plt.close()

def generate_report(analysis, output_dir, file_name, narrative):
    """
    Create a markdown report with a narrative analysis
    """
    report_path = os.path.join(output_dir, 'analysis_report.md')

    with open(report_path, 'w') as f:
        f.write(f"# Data Analysis Report for {file_name}\n\n")

        # Add narrative summary
        f.write("## Narrative Analysis\n")
        f.write(narrative)

        # Descriptive Statistics
        f.write("\n## Descriptive Statistics\n")
        for column, stats in analysis['description'].items():
            f.write(f"### {column}\n")
            for stat, value in stats.items():
                f.write(f"- {stat}: {value}\n")

        # Missing Values
        f.write("\n## Missing Values\n")
        for column, count in analysis['missing_values'].items():
            f.write(f"- {column}: {count}\n")

        # Correlation Matrix
        f.write("\n## Correlation Matrix\n")
        f.write("```\n")
        for column, correlations in analysis['correlation'].items():
            f.write(f"{column}: {correlations}\n")
        f.write("```\n")

        # Visualization Links
        f.write("\n## Visualizations\n")
        for img in os.listdir(output_dir):
            if img.endswith(('.png', '.jpg', '.jpeg')):
                f.write(f"![{img}]({img})\n")

def process_csv_files():
    """
    Process all CSV files in the current directory
    """
    csv_files = find_csv_files()

    if not csv_files:
        print("No CSV files found in the current directory.")
        return

    print(f"Found {len(csv_files)} CSV files:")
    for file in csv_files:
        print(f"- {file}")

    for file_path in csv_files:
        try:
            print(f"\nProcessing {file_path}...")

            # Read CSV
            df = safe_read_csv(file_path)

            # Create output directory
            output_dir = os.path.splitext(file_path)[0] + '_analysis'

            # Analyze data
            analysis = analyze_data(df)

            # Generate narrative
            narrative = generate_narrative(df, analysis)

            # Create visualizations
            create_visualizations(df, output_dir, file_path)

            # Generate report with narrative
            generate_report(analysis, output_dir, file_path, narrative)

            print(f"Analysis complete for {file_path}. Results saved in {output_dir}")

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

def main():
    """
    Main function to run the script
    """
    process_csv_files()

if __name__ == "__main__":
    main()
