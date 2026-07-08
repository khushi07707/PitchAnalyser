using AIAugmentedPitchAnalyzer.Domain.Entities;
using System;
using System.Threading.Tasks;

namespace AIAugmentedPitchAnalyzer.Application.Interfaces.IRepository
{
    public interface IStartupRepository : IGenericRepository<Startup>
    {
        Task<Startup?> GetWithPitchesAsync(Guid startupId);
        Task<(IEnumerable<Startup> Items, int TotalCount)> GetPagedAsync(int pageNumber, int pageSize, Domain.Enums.Industry? industry = null, string? search = null);
    }
}
