# Filter Templates & Configuration Library

## Target Profile Filter (Student/Intern Jobs)

Used to flag job postings that match a specific profile (students, interns, no experience required).

### Configuration

Add to `config/filters.yaml`:

```yaml
target_profile:
  keywords: [
    "인턴", "인턴십", "신입", "무경력", "초보", "경력무관",
    "학생", "대학생", "재학생", "졸업예정", "졸업예정자",
    "intern", "internship", "entry level", "junior", "no experience",
    "student", "undergraduate", "graduate student", "final year"
  ]
  emoji: "🎯"
