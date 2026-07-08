using System.Collections.Generic;

namespace AIAugmentedPitchAnalyzer.Shared.Responses
{
    public class PagedResult<T>
    {
        public IEnumerable<T> Items { get; set; } = new List<T>();
        public int TotalCount { get; set; }
        public int PageNumber { get; set; }
        public int PageSize { get; set; }
        public int TotalPages { get; set; }
        public string? NextPageUrl { get; set; }
        public string? PrevPageUrl { get; set; }
        public string? FirstPageUrl { get; set; }
        public string? LastPageUrl { get; set; }
    }
}
