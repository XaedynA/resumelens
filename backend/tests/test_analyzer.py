from app.analyzer import analyze, contains_term, extract_skills

def test_matching():
    result = analyze("Built Python and SQL automation with Git.", "Need Python, SQL, Docker")
    assert result["matched_skills"] == ["Python", "SQL"]
    assert result["missing_skills"] == ["Docker"]
    assert 0 <= result["score"] <= 100

def test_no_false_java_match():
    assert "Java" not in extract_skills("JavaScript and TypeScript")

def test_csharp_detected():
    assert contains_term("Used C# and .NET", "c#")

def test_empty():
    try:
        analyze("", "Python")
        assert False
    except ValueError:
        pass

def test_no_skills_fallback():
    result = analyze("Wrote reports and organized records", "organize records")
    assert result["score"] is None  # Not enough recognized requirements
