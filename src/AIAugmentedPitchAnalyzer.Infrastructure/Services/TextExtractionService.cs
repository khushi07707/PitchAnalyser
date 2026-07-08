using AIAugmentedPitchAnalyzer.Application.Interfaces.IServices;
using AIAugmentedPitchAnalyzer.Shared.Responses;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Presentation;
using System;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using UglyToad.PdfPig;
using DrawingText = DocumentFormat.OpenXml.Drawing.Text;

namespace AIAugmentedPitchAnalyzer.Infrastructure.Services
{
    public class TextExtractionService : ITextExtractionService
    {
        public async Task<ApiResponse<string>> ExtractTextFromFileAsync(string filePath, string? contentType = null)
        {
            if (!File.Exists(filePath))
            {
                return new ApiResponse<string> { Success = false, Message = "File not found" };
            }

            try
            {
                var ext = System.IO.Path.GetExtension(filePath).ToLowerInvariant();
                if (ext == ".pdf" || (contentType?.Contains("pdf", StringComparison.OrdinalIgnoreCase) == true))
                {
                    return await Task.Run(() => ExtractPdfText(filePath));
                }

                if (ext == ".pptx" || ext == ".ppt" || (contentType?.Contains("presentation", StringComparison.OrdinalIgnoreCase) == true))
                {
                    return await Task.Run(() => ExtractPptxText(filePath));
                }

                return new ApiResponse<string> { Success = false, Message = "Unsupported file type for extraction" };
            }
            catch (Exception ex)
            {
                return new ApiResponse<string> { Success = false, Message = ex.Message };
            }
        }

        private ApiResponse<string> ExtractPdfText(string filePath)
        {
            var sb = new StringBuilder();
            using var document = PdfDocument.Open(filePath);
            foreach (var page in document.GetPages())
            {
                var text = page.Text;
                if (!string.IsNullOrWhiteSpace(text))
                {
                    sb.AppendLine(text);
                }
            }

            return new ApiResponse<string> { Data = CleanExtractedText(sb.ToString()) };
        }

        private ApiResponse<string> ExtractPptxText(string filePath)
        {
            var sb = new StringBuilder();
            using var presentation = PresentationDocument.Open(filePath, false);
            var slides = presentation.PresentationPart?.SlideParts;
            if (slides != null)
            {
                foreach (var slidePart in slides)
                {
                    var texts = slidePart.Slide.Descendants<DrawingText>();
                    foreach (var text in texts)
                    {
                        if (!string.IsNullOrWhiteSpace(text.Text))
                        {
                            sb.AppendLine(text.Text);
                        }
                    }
                }
            }

            return new ApiResponse<string> { Data = CleanExtractedText(sb.ToString()) };
        }

        private string CleanExtractedText(string text)
        {
            if (string.IsNullOrWhiteSpace(text)) return string.Empty;

            text = Regex.Replace(text, "\r\n|\r|\n", "\n");
            text = Regex.Replace(text, "\n{2,}", "\n\n");
            text = Regex.Replace(text, "[ \t]{2,}", " ");
            return text.Trim();
        }
    }
}
