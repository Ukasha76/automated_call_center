#!/usr/bin/env python
# filepath: d:\FYP\server\agents\graph\test.py

import asyncio
import sys
import os
import pandas as pd
from main import MedicalGraphSystem
import time
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_groq import ChatGroq

class GraphRAGTester:
    def __init__(self):
        self.graph_system = MedicalGraphSystem()
        print("✅ Medical Graph System initialized")
        
    async def test_query(self, query):
        print(f"\n🔍 Testing query: '{query}'")
        
        try:
            result = await self.graph_system.handle_query({"text": query})
            
            print("\n📊 Results:")
            print("-" * 50)
            print(f"Response: {result['response']}")
            
            if 'context_updates' in result:
                entities = result['context_updates'].get('active_entities', [])
                if entities:
                    print("\nExtracted entities:")
                    for entity in entities[:5]:  # Show up to 5 entities
                        if isinstance(entity, dict):
                            print(f"- {entity.get('name', 'Unknown')} ({entity.get('type', 'Unknown')})")
            
            return result
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None

# Updated test_from_csv function for storing Cypher queries in context
async def test_from_csv(csv_path, max_samples=300, batch_size=5, delay_between_batches=2):
    """Process queries from a CSV file and save responses with Cypher queries in context column."""
    if not os.path.exists(csv_path):
        print(f"❌ Error: CSV file not found at '{csv_path}'")
        return
    
    # Read the CSV file
    print(f"Loading queries from: {csv_path}")
    df = pd.read_csv(csv_path)
    
    if 'question' not in df.columns:
        print("❌ Error: CSV must contain a 'question' column")
        return
    
    # Create response and context columns if they don't exist
    if 'response' not in df.columns:
        df['response'] = ""
    if 'context' not in df.columns:
        df['context'] = ""
    
    # Limit samples to max_samples
    if len(df) > max_samples:
        print(f"⚠️ CSV contains {len(df)} queries. Processing only the first {max_samples}.")
        df = df.head(max_samples)
    
    # Initialize components needed for Cypher generation
    llm = ChatGroq(
        model_name="gemma2-9b-it",
        temperature=0.2,
        api_key=os.getenv("GROQ_API_KEY"),
    )
    
    # Create prompt template for Cypher generation
    examples = [
        {"question": "How many diseases are there?", "query": "MATCH (d:Disease) RETURN count(d);"},
        {"question": "Symptoms of COVID-19?", "query": "MATCH (s:Symptom)-[:SYMPTOM_OF]->(d:Disease {name: 'COVID-19'}) RETURN s.name;"},
        {"question": "Drugs for Diabetes?", "query": "MATCH (d:Disease {name: 'Diabetes'})<-[:PRESCRIBED_FOR]-(drug:Drug) RETURN drug.name;"},
        {"question": "Side effects of a drug?", "query": "MATCH (drug:Drug {name: 'Drug Name'}) MATCH (se:SideEffect)<-[:HAS_SIDE_EFFECT]-(t:Treatment)-[:USES_DRUG]->(drug) RETURN se.name;"},
        {"question": "Treatments for a disease?", "query": "MATCH (t:Treatment)-[:TREATS]->(d:Disease {name: 'Disease Name'}) OPTIONAL MATCH (t)-[:USES_DRUG]->(drug:Drug) RETURN t.name, drug.name;"}
    ]

    schema = """Node properties:
Disease {name: STRING}, Symptom {name: STRING}, GeneticLinkage {name: STRING}, 
CareInstruction {name: STRING}, Drug {name: STRING}, Treatment {name: STRING}, 
SideEffect {name: STRING}.

Relationships:
(:Symptom)-[:SYMPTOM_OF]->(:Disease), 
(:GeneticLinkage)-[:LINKED_TO]->(:Disease), 
(:CareInstruction)-[:RECOMMENDED_FOR]->(:Disease), 
(:Drug)-[:PRESCRIBED_FOR]->(:Disease), 
(:Drug)-[:RECOMMENDED_DOSAGE]->(:Disease), 
(:Treatment)-[:TREATS]->(:Disease), 
(:Treatment)-[:USES_DRUG]->(:Drug), 
(:Treatment)-[:HAS_SIDE_EFFECT]->(:SideEffect)."""

    example_prompt = PromptTemplate.from_template(
        "User input: {question}\nCypher query: {query}"
    )

    prompt = FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
        prefix="""You are a Neo4j expert. Generate ONLY the Cypher query - no additional text or markdown. 

Important rules:
1. Always use single quotes for string values
2. Always end queries with a semicolon
3. Never include markdown code blocks
4. Use correct relationship types from schema

Schema:
{schema}

Examples:""",
        suffix="User input: {question}\nCypher query:",
        input_variables=["question", "schema"],
    )
    
    # Initialize tester
    tester = GraphRAGTester()
    
    # Calculate number of batches
    num_batches = (len(df) + batch_size - 1) // batch_size  # Ceiling division
    
    # Process each query in batches
    print(f"\n=== 🧪 PROCESSING {len(df)} QUERIES IN {num_batches} BATCHES ===")
    print(f"Batch size: {batch_size}, Delay between batches: {delay_between_batches}s")
    
    for batch_idx in num_batches:
        batch_start = batch_idx * batch_size
        batch_end = min(batch_start + batch_size, len(df))
        
        print(f"\n🔄 Processing batch {batch_idx+1}/{num_batches} (queries {batch_start+1}-{batch_end})")
        
        # Process each query in this batch
        for idx in range(batch_start, batch_end):
            row = df.iloc[idx]
            query = row['question']
            print(f"\n[{idx+1}/{len(df)}] Processing: '{query[:50]}{'...' if len(query) > 50 else ''}'")
            
            # Skip empty queries
            if pd.isna(query) or not query.strip():
                print("⚠️ Skipping empty query")
                continue
            
            # Generate Cypher query for this question
            try:
                # Format prompt with the question
                formatted_prompt = prompt.format(
                    question=query,
                    schema=schema
                )
                # Generate Cypher query
                response = await llm.ainvoke(formatted_prompt)
                if response and hasattr(response, 'content'):
                    cypher_query = response.content
                    # Clean up the query
                    cypher_query = clean_cypher_query(cypher_query)
                    # Store in context
                    df.at[idx, 'context'] = f"CYPHER: {cypher_query}"
                    print(f"✓ Generated Cypher: {cypher_query}")
                else:
                    df.at[idx, 'context'] = "ERROR: Failed to generate Cypher query"
                    print("✗ Failed to generate Cypher query")
            except Exception as e:
                df.at[idx, 'context'] = f"ERROR: {str(e)}"
                print(f"✗ Error generating Cypher: {str(e)}")
            
            # Process the query with the agent
            try:
                result = await tester.test_query(query)
                
                if result and 'response' in result:
                    # Update the dataframe with the response
                    df.at[idx, 'response'] = result['response']
                    print(f"✅ Response saved for query #{idx+1}")
                else:
                    df.at[idx, 'response'] = "ERROR: Failed to get response"
                    print(f"❌ Failed to get response for query #{idx+1}")
            except Exception as e:
                df.at[idx, 'response'] = f"ERROR: {str(e)}"
                print(f"❌ Error processing query: {str(e)}")
        
        # Save after each batch
        df.to_csv(csv_path, index=False)
        print(f"💾 Batch {batch_idx+1}/{num_batches} completed and saved to {csv_path}")
        
        # Add delay between batches (except after the last batch)
        if batch_idx < num_batches - 1:
            print(f"⏱️ Pausing for {delay_between_batches}s before next batch...")
            time.sleep(delay_between_batches)
    
    print(f"\n✅ All {len(df)} queries processed in {num_batches} batches and saved to: {csv_path}")
    return df

# Helper function for cleaning Cypher queries
def clean_cypher_query(query: str) -> str:
    """Clean and validate Cypher queries"""
    # Remove markdown code blocks if present
    if query.startswith("```cypher"):
        query = query[9:]  # Remove ```cypher
    if query.endswith("```"):
        query = query[:-3]  # Remove ```
    
    # Fix common syntax issues
    query = query.strip()
    query = query.replace('"', "'")  # Standardize quotes
    query = query.replace("SYMPTOMM_OF", "SYMPTOM_OF")  # Fix relationship typo
    query = query.replace(
        "MATCH (s:Symptom {name: 'coughing'}) OR (s:Symptom {name: 'chest discomfort'})",
        "MATCH (s:Symptom)\nWHERE s.name = 'coughing' OR s.name = 'chest discomfort'"
    )  # Correct Cypher syntax
    query = query.replace(
        "RETURN t.name, drug.name, drug.name;",
        "RETURN t.name, drug.name;"
    )  # Correct Cypher syntax
    
    # Ensure query ends with semicolon
    if not query.endswith(";"):
        query += ";"
    
    return query

async def main():
    # Check if CSV file is provided
    if len(sys.argv) > 1 and sys.argv[1].endswith('.csv'):
        # Process queries from CSV
        csv_path = sys.argv[1]
        
        # Get optional parameters
        max_samples = 300  # Default max samples
        batch_size = 5     # Default batch size
        delay = 2          # Default delay
        
        # Check for custom parameters
        if len(sys.argv) > 2:
            try:
                batch_size = int(sys.argv[2])
                if len(sys.argv) > 3:
                    delay = float(sys.argv[3])
            except ValueError:
                print("⚠️ Invalid parameters. Using defaults.")
                
        await test_from_csv(csv_path, max_samples=max_samples, batch_size=batch_size, delay_between_batches=delay)
    else:
        # If no CSV provided, run the existing test logic or prompt for CSV
        if len(sys.argv) <= 1:
            print("\n=== 📄 CSV TEST MODE ===")
            csv_path = input("Enter path to CSV file with queries: ").strip()
            
            if csv_path and os.path.exists(csv_path):
                # Get batch parameters
                batch_size = input("Enter batch size (default: 5): ").strip()
                batch_size = int(batch_size) if batch_size.isdigit() else 5
                
                delay = input("Enter delay between batches in seconds (default: 2): ").strip()
                delay = float(delay) if delay.replace('.', '').isdigit() else 2
                
                await test_from_csv(csv_path, batch_size=batch_size, delay_between_batches=delay)
            else:
                print("❌ Invalid CSV path or file not found")
                return
        else:
            # Run single query test if arguments provided but not a CSV
            tester = GraphRAGTester()
            query = " ".join(sys.argv[1:])
            await tester.test_query(query)

if __name__ == "__main__":
    asyncio.run(main())