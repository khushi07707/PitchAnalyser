using AIAugmentedPitchAnalyzer.Application.Interfaces.IRepository;
using AIAugmentedPitchAnalyzer.Domain.Entities;
using AIAugmentedPitchAnalyzer.Persistence.Context;
using Microsoft.EntityFrameworkCore;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace AIAugmentedPitchAnalyzer.Persistence.Repositories
{
    public class PitchRepository : GenericRepository<Pitch>, IPitchRepository
    {
        public PitchRepository(ApplicationDbContext context) : base(context)
        {
        }

        public async Task<Pitch?> GetByIdWithAnalysisAsync(Guid id)
        {
            return await _dbSet
                .Include(p => p.Analysis)
                .FirstOrDefaultAsync(p => p.Id == id);
        }

        public async Task<IEnumerable<Pitch>> GetAllWithAnalysisAsync()
        {
            return await _dbSet
                .AsNoTracking()
                .Include(p => p.Analysis)
                .ToListAsync();
        }

        public async Task<IEnumerable<Pitch>> GetByStartupIdAsync(Guid startupId)
        {
            return await _dbSet
                .AsNoTracking()
                .Include(p => p.Analysis)
                .Where(p => p.StartupId == startupId)
                .ToListAsync();
        }
    }
}
