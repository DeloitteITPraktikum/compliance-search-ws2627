import parse_pdf
import save_json
document_parsed = parse_pdf.parse_pdf("C:/Users/timsi/source/repos/DeloitteITPraktikum/compliance-search-ws2627/setup/downloads/32025R0532_DE.pdf")
save_json.save_json(document_parsed, "C:/Users/timsi/source/repos/DeloitteITPraktikum/compliance-search-ws2627/backend/src/compliance_search/processing/Parsing/Parsed_Test/")