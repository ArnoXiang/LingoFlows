/**
 * 报价提取服务 - 提供从各类文件中提取报价信息的函数
 * 
 * 这是前端的示例实现，实际生产环境中应该由后端完成
 * 这里提供的是一个框架，供后端开发人员参考
 */
import * as XLSX from 'xlsx';

/**
 * 根据文件类型选择合适的提取器
 * @param {Object} file 文件对象
 * @param {String} fileType 文件MIME类型
 * @returns {Object} 提取的报价信息
 */
export const extractQuoteFromFile = async (file, fileType) => {
  console.log('Extracting quote from file:', file, 'type:', fileType);
  
  // 根据文件类型选择提取器
  if (fileType.includes('excel') || fileType.includes('spreadsheet') || 
      file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
    return extractFromExcel(file);
  } else if (fileType.includes('csv')) {
    return extractFromCSV(file);
  } else if (fileType.includes('pdf')) {
    return extractFromPDF(file);
  } else if (fileType.includes('word') || fileType.includes('document')) {
    return extractFromWord(file);
  } else {
    throw new Error('Unsupported file type: ' + fileType);
  }
};

/**
 * 从Excel文件中提取报价信息
 * @param {Object} file Excel文件对象
 * @returns {Object} 提取的报价信息
 */
const extractFromExcel = async (file) => {
  console.log('Extracting from Excel file:', file);
  
  try {
    // 使用FileReader读取文件内容
    const data = await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(new Uint8Array(e.target.result));
      reader.onerror = (e) => reject(new Error('Failed to read file'));
      reader.readAsArrayBuffer(file);
    });
    
    // 使用xlsx库解析Excel文件
    const workbook = XLSX.read(data, { type: 'array' });
    
    // 检查是否存在名为"Log"的表格
    if (!workbook.SheetNames.includes('Log')) {
      console.warn('No "Log" sheet found in the Excel file');
      // 尝试使用第一个sheet
      if (workbook.SheetNames.length > 0) {
        console.log('Using the first sheet instead:', workbook.SheetNames[0]);
      } else {
        throw new Error('Excel file does not contain any sheets');
      }
    }
    
    // 获取"Log"表格内容，如果不存在则使用第一个表格
    const sheetName = workbook.SheetNames.includes('Log') ? 'Log' : workbook.SheetNames[0];
    const sheet = workbook.Sheets[sheetName];
    
    // 将表格转换为JSON对象数组
    const jsonData = XLSX.utils.sheet_to_json(sheet, { 
      header: 1,  // 使用1-indexed数组作为header
      defval: '',  // 默认值为空字符串
      blankrows: false,  // 忽略空行
      raw: false  // 不使用raw值，转换为字符串以便统一处理
    });
    
    console.log('Extracted sheet data:', jsonData);
    
    // 初始化提取的数据
    let extractedData = {
      quoteAmount: 0,
      currency: 'USD',
      wordCount: 0,
      unitPrice: 0,
      sourceLanguage: '',
      targetLanguages: [],
      weightedCount: 0
    };
    
    // 查找表头行索引（包含Source、Target等的行）
    let headerRowIndex = -1;
    for (let i = 0; i < jsonData.length; i++) {
      const row = jsonData[i];
      // 检查这一行是否包含Source和Target
      if (row.includes('Source') && row.includes('Target')) {
        headerRowIndex = i;
        break;
      }
    }
    
    if (headerRowIndex === -1) {
      console.warn('Header row not found, trying alternative search');
      // 尝试更宽松的搜索
      for (let i = 0; i < jsonData.length; i++) {
        const row = jsonData[i].join(' ').toLowerCase();
        if (row.includes('source') && row.includes('target')) {
          headerRowIndex = i;
          break;
        }
      }
    }
    
    console.log('Header row index:', headerRowIndex);
    
    // 如果找到了表头行
    if (headerRowIndex !== -1) {
      const headers = jsonData[headerRowIndex];
      
      // 查找各列的索引
      const sourceIndex = headers.indexOf('Source');
      const targetIndex = headers.indexOf('Target');
      const totalIndex = headers.indexOf('Total');
      const weightedIndex = headers.indexOf('Weighted');
      
      console.log('Column indices:', {
        sourceIndex, targetIndex, totalIndex, weightedIndex
      });
      
      // 处理每一行数据（排除表头行）
      for (let i = headerRowIndex + 1; i < jsonData.length; i++) {
        const row = jsonData[i];
        // 跳过空行或格式不符的行
        if (!row || row.length <= Math.max(sourceIndex, targetIndex, totalIndex, weightedIndex)) {
          continue;
        }
        
        // 检查是否是Grand Total行
        const rowStr = row.join(' ').toLowerCase();
        if (rowStr.includes('grand total')) {
          // 尝试提取总金额
          const lastCell = row[row.length - 1];
          if (lastCell) {
            // 尝试将值转换为数字
            const numericValue = parseFloat(String(lastCell).replace(/[^0-9.]/g, ''));
            if (!isNaN(numericValue)) {
              extractedData.quoteAmount = numericValue;
              console.log('Found Grand Total amount:', numericValue);
            }
          }
          continue; // 跳过这一行的后续处理
        }
        
        // 提取Source语言（只提取第一行的，后面的可能重复）
        if (sourceIndex !== -1 && row[sourceIndex] && !extractedData.sourceLanguage) {
          extractedData.sourceLanguage = row[sourceIndex];
          console.log('Found source language:', extractedData.sourceLanguage);
        }
        
        // 提取Target语言（可能有多个）
        if (targetIndex !== -1 && row[targetIndex]) {
          const targetLang = row[targetIndex];
          if (!extractedData.targetLanguages.includes(targetLang)) {
            extractedData.targetLanguages.push(targetLang);
            console.log('Found target language:', targetLang);
          }
        }
        
        // 累加Total值
        if (totalIndex !== -1 && row[totalIndex]) {
          const totalValue = parseFloat(String(row[totalIndex]).replace(/[^0-9.]/g, ''));
          if (!isNaN(totalValue)) {
            extractedData.wordCount += totalValue;
          }
        }
        
        // 累加Weighted值
        if (weightedIndex !== -1 && row[weightedIndex]) {
          const weightedValue = parseFloat(String(row[weightedIndex]).replace(/[^0-9.]/g, ''));
          if (!isNaN(weightedValue)) {
            extractedData.weightedCount += weightedValue;
          }
        }
      }
      
      // 如果没找到Grand Total金额，再尝试从最后几行寻找
      if (extractedData.quoteAmount === 0) {
        for (let i = jsonData.length - 1; i >= 0; i--) {
          const row = jsonData[i];
          if (!row || row.length === 0) continue;
          
          const rowStr = row.join(' ').toLowerCase();
          // 特别处理"Grand Total in USD $842.21"这种格式
          if (rowStr.includes('grand total') || rowStr.includes('usd')) {
            console.log('Found potential Grand Total row:', row);
            
            // 方法1: 直接查找包含$的单元格
            for (let j = 0; j < row.length; j++) {
              const cell = String(row[j] || '');
              if (cell.includes('$')) {
                const numericValue = parseFloat(cell.replace(/[^0-9.]/g, ''));
                if (!isNaN(numericValue) && numericValue > 0) {
                  extractedData.quoteAmount = numericValue;
                  console.log('Found Grand Total amount with $ sign:', numericValue);
                  break;
                }
              }
            }
            
            // 如果没找到$符号，尝试其他方法
            if (extractedData.quoteAmount === 0) {
              // 方法2: 查找包含数字的最后一个单元格
              for (let j = row.length - 1; j >= 0; j--) {
                const cell = String(row[j] || '');
                if (/\d+(\.\d+)?/.test(cell)) {
                  const numericValue = parseFloat(cell.replace(/[^0-9.]/g, ''));
                  if (!isNaN(numericValue) && numericValue > 0) {
                    extractedData.quoteAmount = numericValue;
                    console.log('Found Grand Total amount (numeric cell):', numericValue);
                    break;
                  }
                }
              }
            }
            
            // 方法3: 如果是"Grand Total in USD"行，检查下一行是否包含金额
            if (extractedData.quoteAmount === 0 && rowStr.includes('grand total in usd')) {
              if (i + 1 < jsonData.length) {
                const nextRow = jsonData[i + 1];
                if (nextRow && nextRow.length > 0) {
                  // 尝试从下一行提取金额
                  for (let j = 0; j < nextRow.length; j++) {
                    const cell = String(nextRow[j] || '');
                    if (cell.includes('$') || /\d+(\.\d+)?/.test(cell)) {
                      const numericValue = parseFloat(cell.replace(/[^0-9.]/g, ''));
                      if (!isNaN(numericValue) && numericValue > 0) {
                        extractedData.quoteAmount = numericValue;
                        console.log('Found Grand Total amount (next row):', numericValue);
                        break;
                      }
                    }
                  }
                }
              }
            }
            
            if (extractedData.quoteAmount > 0) break;
          }
        }
      }
      
      // 如果仍然没找到金额，尝试在最后一行寻找
      if (extractedData.quoteAmount === 0 && jsonData.length > 0) {
        const lastRow = jsonData[jsonData.length - 1];
        if (lastRow && lastRow.length > 0) {
          // 查找最后一行中的数字
          for (let j = 0; j < lastRow.length; j++) {
            const cell = String(lastRow[j] || '');
            if (cell.includes('$') || /\d+(\.\d+)?/.test(cell)) {
              const numericValue = parseFloat(cell.replace(/[^0-9.]/g, ''));
              if (!isNaN(numericValue) && numericValue > 0) {
                extractedData.quoteAmount = numericValue;
                console.log('Found amount in last row:', numericValue);
                break;
              }
            }
          }
        }
      }
    }
    
    // 如果有总字数和总金额，计算单价
    if (extractedData.wordCount > 0 && extractedData.quoteAmount > 0) {
      extractedData.unitPrice = extractedData.quoteAmount / extractedData.wordCount;
    }
    
    console.log('Final extracted data:', extractedData);
    return extractedData;
    
  } catch (error) {
    console.error('Error extracting from Excel:', error);
    throw error;
  }
};

/**
 * 从CSV文件中提取报价信息
 * @param {Object} file CSV文件对象
 * @returns {Object} 提取的报价信息
 */
const extractFromCSV = async (file) => {
  // 这里是示例代码，实际实现应该使用适当的库解析CSV
  console.log('Extracting from CSV file:', file);
  
  /* 
  后端实现示例代码:
  
  import pandas as pd
  
  def extract_from_csv(file_path):
      # 读取CSV文件
      df = pd.read_csv(file_path)
      
      # 使用与Excel相同的逻辑查找报价信息
      # ...
      
      return {
          'quoteAmount': quote_amount,
          'currency': currency,
          'wordCount': word_count,
          'unitPrice': unit_price
      }
  */
  
  // 模拟提取的数据
  return {
    quoteAmount: 750.00,
    currency: 'EUR',
    wordCount: 3000,
    unitPrice: 0.25
  };
};

/**
 * 从PDF文件中提取报价信息
 * @param {Object} file PDF文件对象
 * @returns {Object} 提取的报价信息
 */
const extractFromPDF = async (file) => {
  // 这里是示例代码，实际实现应该使用适当的库解析PDF
  console.log('Extracting from PDF file:', file);
  
  /* 
  后端实现示例代码:
  
  import PyPDF2
  import re
  
  def extract_from_pdf(file_path):
      with open(file_path, 'rb') as file:
          # 创建PDF阅读器对象
          reader = PyPDF2.PdfReader(file)
          
          # 提取所有文本
          text = ""
          for page_num in range(len(reader.pages)):
              text += reader.pages[page_num].extract_text()
          
          # 使用正则表达式查找关键信息
          amount_match = re.search(r'(?:Total|Amount)[^\d]*(\d+[\d,.]*)', text, re.IGNORECASE)
          currency_match = re.search(r'(?:Currency|in)[\s:]*([A-Z]{3})', text, re.IGNORECASE)
          word_count_match = re.search(r'(?:Word Count|Words)[^\d]*(\d+[\d,.]*)', text, re.IGNORECASE)
          
          quote_amount = float(amount_match.group(1).replace(',', '')) if amount_match else None
          currency = currency_match.group(1) if currency_match else None
          word_count = int(word_count_match.group(1).replace(',', '')) if word_count_match else None
          
          # 计算单价
          unit_price = quote_amount / word_count if quote_amount and word_count else None
          
          return {
              'quoteAmount': quote_amount,
              'currency': currency,
              'wordCount': word_count,
              'unitPrice': unit_price
          }
  */
  
  // 模拟提取的数据
  return {
    quoteAmount: 2000.00,
    currency: 'USD',
    wordCount: 8000,
    unitPrice: 0.25
  };
};

/**
 * 从Word文档中提取报价信息
 * @param {Object} file Word文档对象
 * @returns {Object} 提取的报价信息
 */
const extractFromWord = async (file) => {
  // 这里是示例代码，实际实现应该使用适当的库解析Word文档
  console.log('Extracting from Word file:', file);
  
  /* 
  后端实现示例代码:
  
  import docx
  import re
  
  def extract_from_word(file_path):
      # 读取Word文档
      doc = docx.Document(file_path)
      
      # 提取所有文本
      text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
      
      # 使用与PDF相同的正则表达式查找关键信息
      # ...
      
      return {
          'quoteAmount': quote_amount,
          'currency': currency,
          'wordCount': word_count,
          'unitPrice': unit_price
      }
  */
  
  // 模拟提取的数据
  return {
    quoteAmount: 1500.00,
    currency: 'GBP',
    wordCount: 6000,
    unitPrice: 0.25
  };
};

/**
 * 从文本中提取报价信息的通用函数
 * @param {String} text 要分析的文本
 * @returns {Object} 提取的报价信息
 */
export const extractQuoteFromText = (text) => {
  // 使用正则表达式从文本中提取信息
  const amountMatch = text.match(/(?:total|amount|price)[^\d]*(\d+[\d,.]*)/i);
  const currencyMatch = text.match(/(?:currency|in)[\s:]*([A-Z]{3})/i);
  const wordCountMatch = text.match(/(?:word count|words)[^\d]*(\d+[\d,.]*)/i);
  
  // 解析匹配结果
  const quoteAmount = amountMatch ? parseFloat(amountMatch[1].replace(',', '')) : null;
  const currency = currencyMatch ? currencyMatch[1] : null;
  const wordCount = wordCountMatch ? parseInt(wordCountMatch[1].replace(',', '')) : null;
  
  // 计算单价（如果可能）
  const unitPrice = (quoteAmount && wordCount) ? quoteAmount / wordCount : null;
  
  return {
    quoteAmount,
    currency,
    wordCount,
    unitPrice
  };
}; 