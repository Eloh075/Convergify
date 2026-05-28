#!/usr/bin/env python3
"""
List all available models from Gemini API
"""
import sys
import google.generativeai as genai
from engines.config import EngineConfig

def main():
    print("=" * 80)
    print("LISTING ALL AVAILABLE GEMINI MODELS")
    print("=" * 80)
    
    # Load API keys
    EngineConfig.validate()
    api_key = EngineConfig.GEMINI_API_KEYS[0]
    
    print(f"\nUsing API key: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        genai.configure(api_key=api_key)
        
        print("\nFetching available models...")
        models = genai.list_models()
        
        print("\n" + "=" * 80)
        print("AVAILABLE MODELS")
        print("=" * 80)
        
        gemini_models = []
        gemma_models = []
        other_models = []
        
        for model in models:
            model_name = model.name
            
            # Get output token limit
            output_limit = "Unknown"
            if hasattr(model, 'output_token_limit'):
                output_limit = f"{model.output_token_limit:,}"
            
            # Get input token limit
            input_limit = "Unknown"
            if hasattr(model, 'input_token_limit'):
                input_limit = f"{model.input_token_limit:,}"
            
            # Categorize
            if 'gemini' in model_name.lower():
                gemini_models.append((model_name, input_limit, output_limit))
            elif 'gemma' in model_name.lower():
                gemma_models.append((model_name, input_limit, output_limit))
            else:
                other_models.append((model_name, input_limit, output_limit))
        
        # Print Gemini models
        if gemini_models:
            print("\n🔷 GEMINI MODELS:")
            print("-" * 80)
            for name, inp, out in gemini_models:
                print(f"\n  {name}")
                print(f"    Input:  {inp} tokens")
                print(f"    Output: {out} tokens")
        
        # Print Gemma models
        if gemma_models:
            print("\n🔶 GEMMA MODELS:")
            print("-" * 80)
            for name, inp, out in gemma_models:
                print(f"\n  {name}")
                print(f"    Input:  {inp} tokens")
                print(f"    Output: {out} tokens")
        
        # Print other models
        if other_models:
            print("\n⚪ OTHER MODELS:")
            print("-" * 80)
            for name, inp, out in other_models:
                print(f"\n  {name}")
                print(f"    Input:  {inp} tokens")
                print(f"    Output: {out} tokens")
        
        # Recommendation
        print("\n" + "=" * 80)
        print("RECOMMENDATION FOR LARGE OUTPUTS")
        print("=" * 80)
        
        # Find models with largest output
        all_models = gemini_models + gemma_models + other_models
        
        # Sort by output token limit
        def get_output_tokens(model_tuple):
            try:
                return int(model_tuple[2].replace(',', ''))
            except:
                return 0
        
        sorted_models = sorted(all_models, key=get_output_tokens, reverse=True)
        
        if sorted_models:
            print("\nTop 3 models by output token limit:\n")
            for i, (name, inp, out) in enumerate(sorted_models[:3], 1):
                print(f"{i}. {name}")
                print(f"   Output: {out} tokens")
                print()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
