import os
from meta_context_studio.src.knowledge_base.analyzer import KnowledgeBaseAnalyzer
from meta_context_studio.src.ingestion.data_models import ReportRequest

REPORT_REQUESTS_DIR = "request_for_report_generation"

def main():
    os.makedirs(REPORT_REQUESTS_DIR, exist_ok=True)

    analyzer = KnowledgeBaseAnalyzer(knowledge_base_path="meta_context_studio/knowledge_base/chroma_db")
    report_requests = analyzer.generate_report_requests()

    if report_requests:
        print(f"Generated {len(report_requests)} report requests. Saving to {REPORT_REQUESTS_DIR}/")
        for req in report_requests:
            filename = f"{req.requested_topic.replace(' ', '_').replace('/', '_').replace(':', '_')}_{req.timestamp}.md"
            file_path = os.path.join(REPORT_REQUESTS_DIR, filename)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"# Report Request: {req.requested_topic}\n\n")
                f.write(f"## Justification\n{req.justification}\n\n")
                f.write(f"## Key Questions\n")
                for q in req.key_questions:
                    f.write(f"- {q}\n")
                f.write(f"\n## Desired Format\n{req.desired_format}\n\n")
                f.write(f"## Priority Level\n{req.priority_level}\n\n")
                if req.suggested_sources:
                    f.write(f"## Suggested Sources\n")
                    for s in req.suggested_sources:
                        f.write(f"- {s}\n")
                    f.write(f"\n")
                f.write(f"Generated by: {req.generated_by}\n")
                f.write(f"Timestamp: {req.timestamp}\n")
            print(f"  - Saved: {filename}")
    else:
        print("No new report requests generated at this time.")

if __name__ == "__main__":
    main()
