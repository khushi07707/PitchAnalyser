using AIAugmentedPitchAnalyzer.Domain.Entities;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace AIAugmentedPitchAnalyzer.Application.Interfaces.IRepository
{
    public interface IPitchRepository : IGenericRepository<Pitch>
    {
        Task<Pitch?> GetByIdWithAnalysisAsync(Guid id);
        Task<IEnumerable<Pitch>> GetAllWithAnalysisAsync();
        Task<IEnumerable<Pitch>> GetByStartupIdAsync(Guid startupId);
    }
}
