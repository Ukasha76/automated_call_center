import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import re
import os
from dotenv import load_dotenv

# Load environment variables (if needed)
load_dotenv()

# Load embedding model for similarity calculations
print("Loading embedding model...")
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def compute_response_metrics(df):
    """Compute basic metrics for responses"""
    # Create a copy to avoid modifying original
    results = df.copy()
    
    # 1. Response length (word count)
    results['response_length'] = results['response'].apply(lambda x: len(str(x).split()) if pd.notna(x) else 0)
    
    # 2. Check if response indicates no information found
    no_info_patterns = [
        r"i couldn't find .*information", 
        r"no .*information.*found", 
        r"no .*data.*available",
        r"couldn't find specific information"
    ]
    results['no_info_found'] = results['response'].apply(
        lambda x: 1 if pd.notna(x) and any(re.search(pattern, str(x).lower()) for pattern in no_info_patterns) else 0
    )
    
    # 3. Calculate text similarity between question and answer
    print("Computing embedding similarities...")
    questions = results['question'].fillna('').tolist()
    responses = results['response'].fillna('').tolist()
    reference = results['response'].fillna('').tolist()
    
    # Generate embeddings
    question_embeddings = model.encode(questions)
    response_embeddings = model.encode(responses)
    reference_embeddings = model.encode(reference)
    
    # Calculate similarity scores
    q_r_similarities = []
    r_ref_similarities = []
    
    for i in range(len(questions)):
        # Question-response similarity
        q_r_sim = cosine_similarity([question_embeddings[i]], [response_embeddings[i]])[0][0]
        q_r_similarities.append(q_r_sim)
        
        # Response-reference similarity
        if pd.notna(reference[i]) and reference[i] != '':
            r_ref_sim = cosine_similarity([response_embeddings[i]], [reference_embeddings[i]])[0][0]
        else:
            r_ref_sim = np.nan
        r_ref_similarities.append(r_ref_sim)
    
    results['question_response_similarity'] = q_r_similarities
    results['response_reference_similarity'] = r_ref_similarities
    
    # 4. Check if the response contains medical terminology
    medical_terms = [
        'symptom', 'disease', 'diagnosis', 'treatment', 'medication', 'therapy', 'condition',
        'chronic', 'acute', 'dose', 'drug', 'patient', 'medical', 'clinical', 'physician'
    ]
    
    results['medical_term_count'] = results['response'].apply(
        lambda x: sum(1 for term in medical_terms if pd.notna(x) and term in str(x).lower())
    )
    
    # 5. Calculate response to query specificity
    results['specific_to_query'] = results.apply(
        lambda row: calculate_specificity(row['question'], row['response']),
        axis=1
    )
    
    return results

def calculate_specificity(question, response):
    """Estimate how specific the response is to the query"""
    if pd.isna(question) or pd.isna(response):
        return 0
        
    # Convert to lowercase strings
    question = str(question).lower()
    response = str(response).lower()
    
    # Extract key terms from question (simple approach)
    question_words = set(question.split())
    stop_words = {'what', 'how', 'when', 'where', 'who', 'why', 'is', 'are', 'the', 'a', 'an', 'in', 'for', 'of', 'to', 'and', 'or', 'do', 'does'}
    key_terms = [w for w in question_words if w not in stop_words and len(w) > 3]
    
    # Count key terms present in response
    count = sum(1 for term in key_terms if term in response)
    
    # Normalize by number of key terms with a minimum of 1
    specificity = count / max(len(key_terms), 1)
    
    # Scale to 0-1 range
    return min(specificity, 1.0)

def create_visualizations(results):
    """Create visualizations for evaluation results"""
    # Create output directory if it doesn't exist
    os.makedirs('evaluation_results', exist_ok=True)
    
    # 1. Overall metrics summary
    plt.figure(figsize=(12, 8))
    
    metrics = {
        'Question-Response Similarity': results['question_response_similarity'].mean(),
        'Response-Reference Similarity': results['response_reference_similarity'].mean(),
        'Specificity Score': results['specific_to_query'].mean(),
        'Information Found Rate': 1 - results['no_info_found'].mean()
    }
    
    # Plot bar chart
    bars = plt.bar(metrics.keys(), metrics.values(), color=['#4CAF50', '#2196F3', '#FFC107', '#F44336'])
    plt.ylim(0, 1)
    plt.title('Graph RAG Performance Metrics')
    plt.ylabel('Score (0-1)')
    
    # Add values on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                 f'{height:.3f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('evaluation_results/overall_metrics.png', dpi=300)
    
    # 2. Response length distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(results['response_length'], bins=20, kde=True)
    plt.axvline(results['response_length'].mean(), color='red', linestyle='--', 
                label=f'Mean: {results["response_length"].mean():.1f} words')
    plt.title('Response Length Distribution')
    plt.xlabel('Word Count')
    plt.ylabel('Frequency')
    plt.legend()
    plt.tight_layout()
    plt.savefig('evaluation_results/response_length.png', dpi=300)
    
    # 3. Correlation heatmap
    plt.figure(figsize=(10, 8))
    correlation_columns = ['question_response_similarity', 'response_reference_similarity', 
                          'specific_to_query', 'response_length', 'medical_term_count']
    corr_matrix = results[correlation_columns].corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
    plt.title('Correlation Between Metrics')
    plt.tight_layout()
    plt.savefig('evaluation_results/correlation_heatmap.png', dpi=300)
    
    # 4. Similarity vs Specificity scatter plot
    plt.figure(figsize=(10, 8))
    plt.scatter(results['question_response_similarity'], 
               results['specific_to_query'], 
               alpha=0.6)
    plt.title('Question-Response Similarity vs. Response Specificity')
    plt.xlabel('Question-Response Similarity')
    plt.ylabel('Response Specificity')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('evaluation_results/similarity_vs_specificity.png', dpi=300)
    
    # 5. No information rate
    no_info_rate = results['no_info_found'].mean() * 100
    plt.figure(figsize=(8, 8))
    plt.pie([no_info_rate, 100-no_info_rate], 
            labels=['No information found', 'Information provided'],
            colors=['#FF9800', '#4CAF50'],
            autopct='%1.1f%%',
            startangle=90)
    plt.axis('equal')
    plt.title('Rate of "No Information Found" Responses')
    plt.tight_layout()
    plt.savefig('evaluation_results/no_info_rate.png', dpi=300)
    
    return metrics

def main():
    """Main evaluation function"""
    # Load the data
    print("Loading data...")
    df = pd.read_csv('agents/graph/generated_qa_results.csv')
    
    # Compute metrics
    print("Computing metrics...")
    results = compute_response_metrics(df)
    
    # Create output directory BEFORE saving files
    print("Creating output directory...")
    os.makedirs('evaluation_results', exist_ok=True)
    
    # Save processed results
    results.to_csv('evaluation_results/graph_evaluation_metrics.csv', index=False)
    
    # Create visualizations
    print("Creating visualizations...")
    metrics = create_visualizations(results)
    
    # Print summary
    print("\nEvaluation Summary:")
    print("-" * 50)
    for metric, value in metrics.items():
        print(f"{metric}: {value:.4f}")
    
    # Additional statistical insights
    print("\nAdditional Insights:")
    print(f"Average response length: {results['response_length'].mean():.1f} words")
    print(f"Medical terminology usage: {results['medical_term_count'].mean():.1f} terms per response")
    print(f"No information rate: {results['no_info_found'].mean() * 100:.1f}% of responses")
    
    print("\nEvaluation completed! Results saved to 'evaluation_results' folder.")

if __name__ == "__main__":
    main()