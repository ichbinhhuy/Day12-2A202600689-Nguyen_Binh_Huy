#!/usr/bin/env python3
"""
Automated grading script for Day 12 Lab
Usage: python grade.py <student-repo-path> <public-url> <api-key>
"""

import sys
import os
import subprocess
import requests
import time
from pathlib import Path

class Grader:
    def __init__(self, repo_path, public_url, api_key):
        self.repo_path = Path(repo_path)
        self.public_url = public_url
        self.api_key = api_key
        self.score = 0
        self.max_score = 60
        self.results = []
    
    def test(self, name, points, func):
        """Run a test and record result"""
        try:
            func()
            self.score += points
            self.results.append(f"✅ {name}: {points}/{points}")
            return True
        except AssertionError as e:
            import traceback
            traceback.print_exc()
            self.results.append(f"❌ {name}: 0/{points} - {e}")
            return False
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.results.append(f"❌ {name}: 0/{points} - Error: {e}")
            return False
    
    def check_file_exists(self, filepath):
        """Check if file exists"""
        assert (self.repo_path / filepath).exists(), f"{filepath} not found"
    
    def check_dockerfile(self):
        """Check Dockerfile quality"""
        dockerfile = (self.repo_path / "Dockerfile").read_text()
        assert "FROM" in dockerfile, "No FROM instruction"
        assert "as builder" in dockerfile.lower(), "Not multi-stage"
        assert "slim" in dockerfile.lower(), "Not using slim image"
    
    def check_docker_compose(self):
        """Check docker-compose.yml"""
        compose = (self.repo_path / "docker-compose.yml").read_text()
        assert "redis:" in compose, "No redis service"
        assert "agent:" in compose or "app:" in compose, "No agent service"
    
    def check_no_secrets(self):
        """Check for hardcoded secrets"""
        # We search inside app/ of the repo_path
        app_path = self.repo_path / "app"
        # Since we are on Windows, we can use a python file check instead of grep to avoid platform issues
        secrets_found = False
        for root, dirs, files in os.walk(app_path):
            for file in files:
                if file.endswith('.py'):
                    content = open(os.path.join(root, file), encoding='utf-8').read()
                    if "sk-" in content:
                        secrets_found = True
                        break
        assert not secrets_found, "Found hardcoded API keys"
    
    def test_health_endpoint(self):
        """Test /health endpoint"""
        r = requests.get(f"{self.public_url}/health", timeout=10)
        assert r.status_code == 200, f"Health check failed: {r.status_code}"
    
    def test_ready_endpoint(self):
        """Test /ready endpoint"""
        r = requests.get(f"{self.public_url}/ready", timeout=10)
        assert r.status_code in [200, 503], f"Ready check failed: {r.status_code}"
    
    def test_auth_required(self):
        """Test authentication is required"""
        r = requests.post(
            f"{self.public_url}/ask",
            json={"question": "test"}
        )
        assert r.status_code == 401, "Should require authentication"
    
    def test_auth_works(self):
        """Test authentication works"""
        r = requests.post(
            f"{self.public_url}/ask",
            headers={"X-API-Key": self.api_key},
            json={"user_id": "test", "question": "Hello"}
        )
        assert r.status_code == 200, f"Auth failed: {r.status_code}"
    
    def test_rate_limiting(self):
        """Test rate limiting"""
        # Send many requests
        for i in range(15):
            r = requests.post(
                f"{self.public_url}/ask",
                headers={"X-API-Key": self.api_key},
                json={"user_id": "test_rate", "question": f"test {i}"}
            )
        
        # Should eventually get rate limited
        assert r.status_code == 429, "Rate limiting not working"
    
    def test_conversation_history(self):
        """Test conversation history"""
        user_id = f"test_{int(time.time())}"
        
        # First message
        r1 = requests.post(
            f"{self.public_url}/ask",
            headers={"X-API-Key": self.api_key},
            json={"user_id": user_id, "question": "My name is Alice"}
        )
        assert r1.status_code == 200
        
        # Second message referencing first
        r2 = requests.post(
            f"{self.public_url}/ask",
            headers={"X-API-Key": self.api_key},
            json={"user_id": user_id, "question": "What is my name?"}
        )
        assert r2.status_code == 200
        # Response should mention Alice (basic check)
        assert "Alice" in r2.json().get("answer", ""), f"History context not preserved. Got: {r2.json().get('answer')}"
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Running automated tests...\n")
        
        # File structure tests
        self.test("Dockerfile exists", 2, 
                  lambda: self.check_file_exists("Dockerfile"))
        self.test("docker-compose.yml exists", 2,
                  lambda: self.check_file_exists("docker-compose.yml"))
        self.test("requirements.txt exists", 1,
                  lambda: self.check_file_exists("requirements.txt"))
        
        # Docker quality tests
        self.test("Multi-stage Dockerfile", 5, self.check_dockerfile)
        self.test("Docker Compose has services", 4, self.check_docker_compose)
        
        # Security tests
        self.test("No hardcoded secrets", 5, self.check_no_secrets)
        self.test("Auth required", 5, self.test_auth_required)
        self.test("Auth works", 5, self.test_auth_works)
        self.test("Rate limiting", 5, self.test_rate_limiting)
        
        # Reliability tests
        self.test("Health endpoint", 3, self.test_health_endpoint)
        self.test("Ready endpoint", 3, self.test_ready_endpoint)
        
        # Functionality tests
        self.test("Conversation history", 5, self.test_conversation_history)
        
        # Deployment test
        self.test("Public URL works", 5, self.test_health_endpoint)
        
        # Print results
        print("\n" + "="*60)
        print("📊 GRADING RESULTS")
        print("="*60)
        for result in self.results:
            print(result)
        print("="*60)
        print(f"🎯 TOTAL SCORE: {self.score}/{self.max_score}")
        print(f"📈 PERCENTAGE: {self.score/self.max_score*100:.1f}%")
        
        if self.score >= self.max_score * 0.7:
            print("✅ PASSED")
        else:
            print("❌ FAILED (need 70% to pass)")
        
        return self.score

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python grade.py <repo-path> <public-url> <api-key>")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    public_url = sys.argv[2].rstrip('/')
    api_key = sys.argv[3]
    
    grader = Grader(repo_path, public_url, api_key)
    score = grader.run_all_tests()
    
    sys.exit(0 if score >= grader.max_score * 0.7 else 1)
