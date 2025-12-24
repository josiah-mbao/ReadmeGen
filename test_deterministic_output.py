#!/usr/bin/env python3
"""
Test script to verify deterministic output from ReadmeGen.

This script runs ReadmeGen multiple times with the same inputs to ensure
the output is consistent and deterministic.
"""

import subprocess
import tempfile
from pathlib import Path

def run_readmegen_test():
    """Run ReadmeGen with fixed inputs and compare outputs."""
    
    # Test inputs
    test_inputs = [
        "Test Project",
        "A test project for deterministic output testing",
        "standard",
        "MIT",
        "n",  # No AI
        "n",  # No GitHub
        "",   # No features
        ""    # No usage example
    ]
    
    outputs = []
    
    # Run ReadmeGen 3 times with same inputs
    for i in range(3):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "README.md"
            
            # Run ReadmeGen with test inputs
            process = subprocess.Popen(
                ["readmegen", "init"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=temp_dir,
            )
            
            # Send test inputs
            stdin_input = "\n".join(test_inputs)
            stdout, stderr = process.communicate(stdin_input)
            
            # Read the generated README
            if output_file.exists():
                with open(output_file, 'r') as f:
                    content = f.read()
                    outputs.append(content)
                    print(f"Run {i+1}: Generated README ({len(content)} characters)")
            else:
                print(f"Run {i+1}: Failed to generate README")
                print(f"Stdout: {stdout}")
                print(f"Stderr: {stderr}")
    
    # Compare outputs
    if len(outputs) == 3:
        if outputs[0] == outputs[1] == outputs[2]:
            print("✅ PASS: All outputs are identical (deterministic)")
            return True
        else:
            print("❌ FAIL: Outputs differ (non-deterministic)")
            print("Comparing Run 1 vs Run 2:")
            for i, (c1, c2) in enumerate(zip(outputs[0], outputs[1])):
                if c1 != c2:
                    print(f"  First difference at character {i}: '{c1}' vs '{c2}'")
                    break
            return False
    else:
        print("❌ FAIL: Could not generate all test outputs")
        return False

if __name__ == "__main__":
    print("🧪 Testing ReadmeGen Deterministic Output")
    print("=" * 50)
    
    success = run_readmegen_test()
    
    if success:
        print("\n🎉 Deterministic output test PASSED!")
    else:
        print("\n💥 Deterministic output test FAILED!")
        exit(1)
